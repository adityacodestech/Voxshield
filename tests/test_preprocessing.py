"""
tests/test_preprocessing.py — VoxShield
==========================================
Unit tests for the audio preprocessing pipeline.

Run:
    pytest tests/test_preprocessing.py -v
"""

import sys
from pathlib import Path
import tempfile

import torch
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_sine_wav(
    path: Path,
    sample_rate: int = 16000,
    duration: float = 3.0,
    channels: int = 1,
    freq: float = 440.0,
) -> None:
    """Write a synthetic sine-wave .wav file for testing."""
    import soundfile as sf
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    if channels == 2:
        wave = np.stack([wave, wave], axis=1)
    sf.write(str(path), wave, sample_rate)


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadAudio:
    def test_loads_mono_wav(self, tmp_path):
        from preprocessing.audio_preprocessor import load_audio
        wav_path = tmp_path / "test_mono.wav"
        _make_sine_wav(wav_path, channels=1)
        waveform, sr = load_audio(wav_path)
        assert waveform.dim() == 2, "Expected (channels, samples)"
        assert waveform.shape[0] == 1
        assert sr == 16000

    def test_loads_stereo_wav(self, tmp_path):
        from preprocessing.audio_preprocessor import load_audio
        wav_path = tmp_path / "test_stereo.wav"
        _make_sine_wav(wav_path, channels=2)
        waveform, sr = load_audio(wav_path)
        assert waveform.shape[0] == 2

    def test_raises_on_missing_file(self):
        from preprocessing.audio_preprocessor import load_audio
        with pytest.raises(Exception):
            load_audio("/nonexistent/path/audio.wav")


class TestToMono:
    def test_stereo_to_mono(self):
        from preprocessing.audio_preprocessor import to_mono
        stereo = torch.randn(2, 16000)
        mono = to_mono(stereo)
        assert mono.shape == (1, 16000)

    def test_mono_unchanged(self):
        from preprocessing.audio_preprocessor import to_mono
        mono_in = torch.randn(1, 16000)
        mono_out = to_mono(mono_in)
        assert mono_out.shape == (1, 16000)
        assert torch.allclose(mono_in, mono_out)


class TestResample:
    def test_downsamples_44100_to_16000(self):
        from preprocessing.audio_preprocessor import resample
        waveform = torch.randn(1, 44100)  # 1 second at 44.1 kHz
        out = resample(waveform, orig_sr=44100, target_sr=16000)
        assert out.shape[1] == pytest.approx(16000, abs=200)

    def test_no_change_if_already_target(self):
        from preprocessing.audio_preprocessor import resample
        waveform = torch.randn(1, 16000)
        out = resample(waveform, orig_sr=16000, target_sr=16000)
        assert torch.allclose(waveform, out)


class TestNormalize:
    def test_peak_is_one(self):
        from preprocessing.audio_preprocessor import normalize
        waveform = torch.randn(1, 16000) * 0.3
        out = normalize(waveform)
        assert abs(out.abs().max().item() - 1.0) < 1e-4

    def test_silent_audio_no_nan(self):
        from preprocessing.audio_preprocessor import normalize
        silent = torch.zeros(1, 16000)
        out = normalize(silent)
        assert not torch.isnan(out).any()


class TestTrimOrPad:
    def test_pads_short_audio(self):
        from preprocessing.audio_preprocessor import trim_or_pad
        short = torch.randn(1, 8000)   # 0.5 sec at 16 kHz
        out = trim_or_pad(short, duration=5.0, sample_rate=16000)
        assert out.shape == (1, 80000)

    def test_trims_long_audio(self):
        from preprocessing.audio_preprocessor import trim_or_pad
        long_ = torch.randn(1, 160000)  # 10 sec
        out = trim_or_pad(long_, duration=5.0, sample_rate=16000)
        assert out.shape == (1, 80000)

    def test_exact_length_unchanged(self):
        from preprocessing.audio_preprocessor import trim_or_pad
        exact = torch.randn(1, 80000)
        out = trim_or_pad(exact, duration=5.0, sample_rate=16000)
        assert out.shape == (1, 80000)


class TestPreprocess:
    def test_output_shape(self, tmp_path):
        from preprocessing.audio_preprocessor import preprocess
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path, sample_rate=44100, duration=7.0, channels=2)
        out = preprocess(wav_path)
        assert out.shape == (1, cfg.SAMPLES_PER_SEGMENT)

    def test_values_in_range(self, tmp_path):
        from preprocessing.audio_preprocessor import preprocess
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path)
        out = preprocess(wav_path)
        assert out.min() >= -1.0 - 1e-4
        assert out.max() <= 1.0 + 1e-4

    def test_raises_on_missing_file(self):
        from preprocessing.audio_preprocessor import preprocess
        with pytest.raises(FileNotFoundError):
            preprocess("/no/such/file.wav")


class TestMelSpectrogram:
    def test_output_shape(self, tmp_path):
        from preprocessing.audio_preprocessor import preprocess
        from preprocessing.feature_extractor import get_mel_spectrogram
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path)
        waveform = preprocess(wav_path)
        mel = get_mel_spectrogram(waveform)
        assert mel.shape[0] == 1, "Expected channel dim = 1"
        assert mel.shape[1] == cfg.N_MELS, f"Expected {cfg.N_MELS} Mel bins"

    def test_no_nan_or_inf(self, tmp_path):
        from preprocessing.audio_preprocessor import preprocess
        from preprocessing.feature_extractor import get_mel_spectrogram
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path)
        waveform = preprocess(wav_path)
        mel = get_mel_spectrogram(waveform)
        assert not torch.isnan(mel).any()
        assert not torch.isinf(mel).any()
