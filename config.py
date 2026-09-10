"""
config.py — VoxShield Voice Detection Module
============================================
Single source of truth for all hyperparameters and paths.

IMPORTANT: Training and inference MUST use identical values.
           Never hard-code any of these constants elsewhere.
"""

import os
from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent

# ── Audio preprocessing ───────────────────────────────────────────────────────
SAMPLE_RATE: int = 16_000          # Hz — standard for speech models
SEGMENT_DURATION: float = 5.0      # seconds — trim shorter / pad longer clips
MONO: bool = True                  # always convert to mono

# ── Mel spectrogram ───────────────────────────────────────────────────────────
N_MELS: int = 128                  # number of Mel filter banks
N_FFT: int = 1024                  # FFT window size
HOP_LENGTH: int = 512              # frames between FFT windows
F_MIN: float = 0.0                 # minimum frequency
F_MAX: float = 8_000.0             # maximum frequency (Nyquist at 16 kHz)

# ── MFCC (exploration / visualization only — not used in CNN baseline) ────────
N_MFCC: int = 40

# ── Dataset paths ─────────────────────────────────────────────────────────────
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REAL_DIR = PROCESSED_DIR / "real"
FAKE_DIR = PROCESSED_DIR / "fake"
SPLITS_DIR = DATA_DIR / "splits"

# ASVspoof 2019 LA — expected raw layout after download
ASVSPOOF_DIR = RAW_DIR / "ASVspoof2019_LA"
ASVSPOOF_TRAIN_DIR = ASVSPOOF_DIR / "ASVspoof2019_LA_train" / "flac"
ASVSPOOF_DEV_DIR = ASVSPOOF_DIR / "ASVspoof2019_LA_dev" / "flac"
ASVSPOOF_EVAL_DIR = ASVSPOOF_DIR / "ASVspoof2019_LA_eval" / "flac"
ASVSPOOF_PROTO_DIR = ASVSPOOF_DIR / "ASVspoof2019_LA_cm_protocols"

# ── Split CSV paths ───────────────────────────────────────────────────────────
TRAIN_CSV = SPLITS_DIR / "train.csv"
VAL_CSV = SPLITS_DIR / "val.csv"
TEST_CSV = SPLITS_DIR / "test.csv"

# ── Dataset split ratios ──────────────────────────────────────────────────────
TRAIN_RATIO: float = 0.70
VAL_RATIO: float = 0.15
TEST_RATIO: float = 0.15

# ── Model / training ──────────────────────────────────────────────────────────
BATCH_SIZE: int = 32
NUM_EPOCHS: int = 50
LEARNING_RATE: float = 1e-3
WEIGHT_DECAY: float = 1e-4
DROPOUT: float = 0.3
NUM_WORKERS: int = 0               # 0 = safe on Windows; increase to 2-4 on Linux/Colab

# ── CNN architecture ──────────────────────────────────────────────────────────
CNN_CHANNELS: list = [32, 64, 128] # out-channels for each conv block
CNN_HIDDEN_DIM: int = 256          # dense layer size

# ── Checkpointing ─────────────────────────────────────────────────────────────
MODELS_DIR = ROOT_DIR / "models_saved"
CHECKPOINT_NAME: str = "voxshield_cnn_v1.pth"
BEST_MODEL_NAME: str = "voxshield_best.pth"

# ── Inference ─────────────────────────────────────────────────────────────────
# Threshold is selected on validation set in training/evaluate.py
# Override here only after you have run threshold selection.
DEFAULT_THRESHOLD: float = 0.5    # replaced after val-set selection
MODEL_VERSION: str = "voxshield-v1"

# ── API ───────────────────────────────────────────────────────────────────────
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000

# ── Derived constants (do not edit) ──────────────────────────────────────────
SAMPLES_PER_SEGMENT: int = int(SAMPLE_RATE * SEGMENT_DURATION)

# Computed spectrogram time dimension
import math
SPEC_TIME_FRAMES: int = 1 + SAMPLES_PER_SEGMENT // HOP_LENGTH


def ensure_dirs() -> None:
    """Create all required directories if they don't exist."""
    for d in [RAW_DIR, REAL_DIR, FAKE_DIR, SPLITS_DIR, MODELS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print("VoxShield config loaded successfully.")
    print(f"  Sample rate      : {SAMPLE_RATE} Hz")
    print(f"  Segment duration : {SEGMENT_DURATION}s  ({SAMPLES_PER_SEGMENT} samples)")
    print(f"  Mel bins         : {N_MELS}")
    print(f"  Spectrogram time : {SPEC_TIME_FRAMES} frames")
    print(f"  Model version    : {MODEL_VERSION}")
