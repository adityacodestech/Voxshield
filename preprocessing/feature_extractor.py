"""
preprocessing/feature_extractor.py — VoxShield
===============================================
Converts a preprocessed waveform into model-ready feature representations.

Mel spectrogram  → used by the CNN baseline (and potentially CNNs in phase 2)
MFCC             → used for learning, visualization, and traditional-ML baseline only

All parameters come from config.py.

Usage:
    from preprocessing.audio_preprocessor import preprocess
    from preprocessing.feature_extractor import get_mel_spectrogram, visualize_mel

    waveform = preprocess("audio.wav")          # (1, SAMPLES_PER_SEGMENT)
    mel = get_mel_spectrogram(waveform)         # (1, N_MELS, T)
"""

import sys
from pathlib import Path

import torch
import torchaudio.transforms as T
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # headless-safe backend

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg


# ─────────────────────────────────────────────────────────────────────────────
# Mel spectrogram — PRIMARY feature used in the CNN baseline
# ─────────────────────────────────────────────────────────────────────────────

class MelSpectrogramExtractor:
    """
    Reusable, stateful extractor.  Instantiate once; call many times.
    Converts raw waveform (1, SAMPLES_PER_SEGMENT) → log-mel spectrogram (1, N_MELS, T).
    """

    def __init__(
        self,
        sample_rate: int = cfg.SAMPLE_RATE,
        n_mels: int = cfg.N_MELS,
        n_fft: int = cfg.N_FFT,
        hop_length: int = cfg.HOP_LENGTH,
        f_min: float = cfg.F_MIN,
        f_max: float = cfg.F_MAX,
    ) -> None:
        self.transform = T.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=n_mels,
            f_min=f_min,
            f_max=f_max,
        )
        self.amplitude_to_db = T.AmplitudeToDB(stype="power", top_db=80)

    def __call__(self, waveform: torch.Tensor) -> torch.Tensor:
        """
        Args:
            waveform: (1, SAMPLES_PER_SEGMENT)  — output of preprocess()

        Returns:
            log_mel: (1, N_MELS, T)  — ready for CNN input
        """
        mel = self.transform(waveform)          # (1, N_MELS, T)
        log_mel = self.amplitude_to_db(mel)     # dB scale
        return log_mel


# Module-level singleton — import and reuse directly
_mel_extractor = MelSpectrogramExtractor()


def get_mel_spectrogram(waveform: torch.Tensor) -> torch.Tensor:
    """
    Convenience function wrapping MelSpectrogramExtractor.

    Args:
        waveform: (1, SAMPLES_PER_SEGMENT)

    Returns:
        log_mel: (1, N_MELS, T)
    """
    return _mel_extractor(waveform)


# ─────────────────────────────────────────────────────────────────────────────
# MFCC — for exploration, visualization, and traditional-ML baseline ONLY
# Not used in CNN baseline training.
# ─────────────────────────────────────────────────────────────────────────────

def get_mfcc(waveform: torch.Tensor) -> np.ndarray:
    """
    Compute MFCC features using librosa.

    Args:
        waveform: (1, SAMPLES_PER_SEGMENT)  — output of preprocess()

    Returns:
        mfccs: numpy array of shape (N_MFCC, T)
    """
    y = waveform.squeeze(0).numpy()  # (SAMPLES_PER_SEGMENT,)
    mfccs = librosa.feature.mfcc(
        y=y,
        sr=cfg.SAMPLE_RATE,
        n_mfcc=cfg.N_MFCC,
        n_fft=cfg.N_FFT,
        hop_length=cfg.HOP_LENGTH,
    )
    return mfccs  # (N_MFCC, T)


# ─────────────────────────────────────────────────────────────────────────────
# Visualization helpers
# ─────────────────────────────────────────────────────────────────────────────

def visualize_waveform(waveform: torch.Tensor, title: str = "Waveform",
                       save_path: str | Path | None = None) -> None:
    """Plot amplitude vs time."""
    y = waveform.squeeze(0).numpy()
    time = np.linspace(0, cfg.SEGMENT_DURATION, len(y))

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(time, y, linewidth=0.5, color="#4A90D9")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title(title)
    ax.set_xlim(0, cfg.SEGMENT_DURATION)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    else:
        plt.show()
    plt.close(fig)


def visualize_mel(waveform: torch.Tensor, title: str = "Mel Spectrogram",
                  save_path: str | Path | None = None) -> None:
    """Plot log-Mel spectrogram as a heatmap."""
    log_mel = get_mel_spectrogram(waveform)        # (1, N_MELS, T)
    mel_np = log_mel.squeeze(0).numpy()            # (N_MELS, T)

    fig, ax = plt.subplots(figsize=(10, 4))
    img = librosa.display.specshow(
        mel_np,
        sr=cfg.SAMPLE_RATE,
        hop_length=cfg.HOP_LENGTH,
        x_axis="time",
        y_axis="mel",
        ax=ax,
        cmap="magma",
    )
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    ax.set_title(title)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    else:
        plt.show()
    plt.close(fig)


def visualize_mfcc(waveform: torch.Tensor, title: str = "MFCC",
                   save_path: str | Path | None = None) -> None:
    """Plot MFCC coefficients as a heatmap."""
    mfcc = get_mfcc(waveform)  # (N_MFCC, T)

    fig, ax = plt.subplots(figsize=(10, 4))
    img = librosa.display.specshow(
        mfcc,
        sr=cfg.SAMPLE_RATE,
        hop_length=cfg.HOP_LENGTH,
        x_axis="time",
        ax=ax,
        cmap="coolwarm",
    )
    fig.colorbar(img, ax=ax)
    ax.set_ylabel("MFCC Coefficient")
    ax.set_title(title)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    else:
        plt.show()
    plt.close(fig)


def compare_real_fake(real_path: str | Path, fake_path: str | Path,
                      save_path: str | Path | None = None) -> None:
    """
    Side-by-side Mel spectrograms of a real and a fake utterance.
    Useful for SIH presentation slides.
    """
    from preprocessing.audio_preprocessor import preprocess

    real_wav = preprocess(real_path)
    fake_wav = preprocess(fake_path)

    real_mel = get_mel_spectrogram(real_wav).squeeze(0).numpy()
    fake_mel = get_mel_spectrogram(fake_wav).squeeze(0).numpy()

    fig, axes = plt.subplots(1, 2, figsize=(16, 4))

    for ax, mel, label, color in zip(
        axes,
        [real_mel, fake_mel],
        ["REAL (Genuine)", "FAKE (AI-Generated)"],
        ["Blues", "Reds"],
    ):
        img = librosa.display.specshow(
            mel,
            sr=cfg.SAMPLE_RATE,
            hop_length=cfg.HOP_LENGTH,
            x_axis="time",
            y_axis="mel",
            ax=ax,
            cmap=color,
        )
        fig.colorbar(img, ax=ax, format="%+2.0f dB")
        ax.set_title(label, fontsize=14, fontweight="bold")

    fig.suptitle("Mel Spectrogram Comparison", fontsize=16, fontweight="bold")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"Saved comparison to {save_path}")
    else:
        plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# CLI quick demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python preprocessing/feature_extractor.py <audio_file> [save_dir]")
        sys.exit(1)

    from preprocessing.audio_preprocessor import preprocess

    audio_path = Path(sys.argv[1])
    save_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    print(f"Extracting features for: {audio_path.name}")
    wav = preprocess(audio_path)
    print(f"  Preprocessed shape: {wav.shape}")

    mel = get_mel_spectrogram(wav)
    print(f"  Mel spectrogram shape: {mel.shape}")

    mfcc = get_mfcc(wav)
    print(f"  MFCC shape: {mfcc.shape}")

    visualize_waveform(wav, title=f"Waveform — {audio_path.name}",
                       save_path=save_dir / "waveform.png")
    visualize_mel(wav, title=f"Mel Spectrogram — {audio_path.name}",
                  save_path=save_dir / "mel_spectrogram.png")
    visualize_mfcc(wav, title=f"MFCC — {audio_path.name}",
                   save_path=save_dir / "mfcc.png")

    print(f"  Saved plots to {save_dir}/")
