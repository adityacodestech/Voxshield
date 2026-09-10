"""
preprocessing/audio_preprocessor.py — VoxShield
================================================
Standardises raw audio into a fixed-length mono 16 kHz tensor.

CRITICAL: The preprocess() function here is the SINGLE implementation used
by both the training pipeline and the production inference endpoint.
Never duplicate this logic; always import from here.

Pipeline:
    load_audio → to_mono → resample → normalize → trim_or_pad → tensor

All parameters are read from config.py.
"""

import sys
from pathlib import Path

import torch
# import torchaudio
import soundfile as sf
import torchaudio.transforms as T

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg


# ─────────────────────────────────────────────────────────────────────────────
# Individual steps
# ─────────────────────────────────────────────────────────────────────────────

# def load_audio(path: str | Path) -> tuple[torch.Tensor, int]:
#     """
#     Load an audio file.

#     Returns:
#         waveform : Tensor of shape (channels, samples)
#         sample_rate : original sample rate
#     """
#     waveform, sample_rate = torchaudio.load(str(path))
#     return waveform, sample_rate

def load_audio(path: str | Path) -> tuple[torch.Tensor, int]:
    """
    Load an audio file using soundfile.

    Returns:
        waveform : Tensor of shape (channels, samples)
        sample_rate : original sample rate
    """
    audio, sample_rate = sf.read(str(path), always_2d=True)

    # soundfile returns (samples, channels)
    waveform = torch.from_numpy(audio.T).float()

    return waveform, sample_rate
def to_mono(waveform: torch.Tensor) -> torch.Tensor:
    """
    Convert multi-channel audio to mono by averaging channels.

    Args:
        waveform: (channels, samples)

    Returns:
        waveform: (1, samples)
    """
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    return waveform


def resample(waveform: torch.Tensor, orig_sr: int,
             target_sr: int = cfg.SAMPLE_RATE) -> torch.Tensor:
    """
    Resample waveform to target sample rate.

    Args:
        waveform : (1, samples)
        orig_sr  : original sample rate
        target_sr: target sample rate (default: cfg.SAMPLE_RATE)

    Returns:
        resampled waveform: (1, new_samples)
    """
    if orig_sr == target_sr:
        return waveform
    resampler = T.Resample(orig_freq=orig_sr, new_freq=target_sr)
    return resampler(waveform)


def normalize(waveform: torch.Tensor, eps: float = 1e-9) -> torch.Tensor:
    """
    Peak-normalize waveform to [-1, 1].

    Args:
        waveform: (1, samples)
        eps     : small constant to avoid division by zero

    Returns:
        normalized waveform: (1, samples)
    """
    peak = waveform.abs().max()
    return waveform / (peak + eps)


def trim_or_pad(
    waveform: torch.Tensor,
    duration: float = cfg.SEGMENT_DURATION,
    sample_rate: int = cfg.SAMPLE_RATE,
) -> torch.Tensor:
    """
    Trim or zero-pad waveform to exactly `duration` seconds.

    Args:
        waveform   : (1, samples)
        duration   : target duration in seconds (from config.py)
        sample_rate: sample rate (from config.py)

    Returns:
        waveform of shape (1, sample_rate * duration)
    """
    target_len = int(sample_rate * duration)
    current_len = waveform.shape[1]

    if current_len > target_len:
        # Trim from centre to preserve more speech content
        start = (current_len - target_len) // 2
        waveform = waveform[:, start: start + target_len]
    elif current_len < target_len:
        # Zero-pad symmetrically (half left, half right)
        pad_total = target_len - current_len
        pad_left = pad_total // 2
        pad_right = pad_total - pad_left
        waveform = torch.nn.functional.pad(waveform, (pad_left, pad_right))

    return waveform


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point — ALWAYS use this for both training and inference
# ─────────────────────────────────────────────────────────────────────────────

def preprocess(path: str | Path) -> torch.Tensor:
    """
    Full preprocessing pipeline.

    Steps:
        1. Load audio file
        2. Convert to mono
        3. Resample to SAMPLE_RATE (16 kHz)
        4. Peak-normalize
        5. Trim or pad to SEGMENT_DURATION (5 s)

    Args:
        path: path to any audio file (.wav, .flac, .mp3, …)

    Returns:
        waveform: Tensor of shape (1, SAMPLES_PER_SEGMENT)
                  dtype=float32, values in [-1, 1]

    Raises:
        FileNotFoundError: if the audio file does not exist
        RuntimeError    : if torchaudio fails to decode the file
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    waveform, sr = load_audio(path)
    waveform = to_mono(waveform)
    waveform = resample(waveform, sr)
    waveform = normalize(waveform)
    waveform = trim_or_pad(waveform)

    assert waveform.shape == (1, cfg.SAMPLES_PER_SEGMENT), (
        f"Unexpected shape after preprocessing: {waveform.shape}"
    )

    return waveform


# ─────────────────────────────────────────────────────────────────────────────
# Quick diagnostic
# ─────────────────────────────────────────────────────────────────────────────

def inspect(path: str | Path) -> None:
    """Print audio metadata before and after preprocessing."""
    path = Path(path)
    raw, sr = load_audio(path)
    print(f"File            : {path.name}")
    print(f"  Original SR   : {sr} Hz")
    print(f"  Channels      : {raw.shape[0]}")
    print(f"  Samples       : {raw.shape[1]}")
    print(f"  Duration      : {raw.shape[1]/sr:.2f}s")

    processed = preprocess(path)
    print(f"  After preproc :")
    print(f"    Shape       : {processed.shape}")
    print(f"    SR          : {cfg.SAMPLE_RATE} Hz")
    print(f"    Duration    : {cfg.SEGMENT_DURATION}s")
    print(f"    Min/Max     : {processed.min():.4f} / {processed.max():.4f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python preprocessing/audio_preprocessor.py <audio_file>")
        sys.exit(1)
    inspect(sys.argv[1])
