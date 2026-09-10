"""
VoiceGuard Competition — Dataset Setup
=======================================
Jalankan sekali di awal notebook untuk download dataset dari HuggingFace.

    !python download_data.py

Atau langsung dari notebook cell:

    exec(open("download_data.py").read())
"""

import os
import sys
import subprocess
from pathlib import Path


def _pip(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])


try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("Installing huggingface_hub...")
    _pip("huggingface_hub")
    from huggingface_hub import snapshot_download

try:
    import pandas as pd
except ImportError:
    _pip("pandas")
    import pandas as pd

try:
    import librosa
except ImportError:
    print("Installing librosa...")
    _pip("librosa")

# ── config ────────────────────────────────────────────────────────────────────
REPO_ID   = "fassabilf/voiceguard-competition"
LOCAL_DIR = Path(".")
HF_TOKEN  = os.environ.get("HF_TOKEN")

# ── download ──────────────────────────────────────────────────────────────────
print("=" * 55)
print("  VoiceGuard — Deepfake Audio Detection Competition")
print("=" * 55)
print(f"Repo : {REPO_ID}")
print(f"Dir  : {LOCAL_DIR.resolve()}")
print()
print("Downloading train/, test/, dan CSV files...")
print("(ini mungkin butuh beberapa menit — ~1.5 GB audio)")

snapshot_download(
    repo_id=REPO_ID,
    repo_type="dataset",
    local_dir=str(LOCAL_DIR),
    token=HF_TOKEN,
    allow_patterns=["train/**", "test/**", "*.csv"],
    ignore_patterns=["*.gitattributes", ".huggingface/**"],
)

# ── verifikasi ────────────────────────────────────────────────────────────────
print()
train_df = pd.read_csv(LOCAL_DIR / "train.csv")
test_df  = pd.read_csv(LOCAL_DIR / "test.csv")

n_real_train = (train_df["label"] == "real").sum()
n_fake_train = (train_df["label"] == "fake").sum()

wav_real = list((LOCAL_DIR / "train" / "real").glob("*.wav"))
wav_fake = list((LOCAL_DIR / "train" / "fake").glob("*.wav"))
wav_test = list((LOCAL_DIR / "test").glob("*.wav"))

print(f"✓ train.csv  : {len(train_df):,} rows")
print(f"   real  : {n_real_train:,}  |  WAV: {len(wav_real):,}")
print(f"   fake  : {n_fake_train:,}  |  WAV: {len(wav_fake):,}")
print(f"✓ test.csv   : {len(test_df):,} rows  |  WAV: {len(wav_test):,}")
print()
print("Submission format: CSV dengan kolom id, score (float 0-1)")
print("  score = P(fake) — bukan binary label!")
print()
print("Dataset siap! Lanjut ke notebook selanjutnya.")
print("=" * 55)
