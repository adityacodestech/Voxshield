"""
training/dataset.py — VoxShield
================================
PyTorch Dataset and DataLoader builders for the VoxShield voice detector.

Responsibilities:
  1. Read data/splits/speaker_manifest.csv (written by scripts/prepare_dataset.py)
  2. Assign partitions using the OFFICIAL ASVspoof train/dev/eval split
     (via filename prefix: train_* → train, dev_* → val, eval_* → test)
  3. Write data/splits/train.csv, val.csv, test.csv
  4. Provide AudioDataset(csv_path) for DataLoader use

Official-partition strategy (preferred for ASVspoof):
    train_* files → train.csv   ← model training
    dev_*   files → val.csv     ← validation + threshold selection
    eval_*  files → test.csv    ← final unseen evaluation

    ASVspoof partitions are speaker-disjoint by design, so this preserves
    both the official benchmark and the speaker-independence guarantee.

Fallback (create_splits_random) for non-ASVspoof datasets:
    Randomly assigns speakers 70/15/15 across splits.
    Speaker A → TRAIN only, Speaker B → VAL only, etc.

CSV format:
    path,label,speaker_id
    data/processed/real/train_LA_T_001.flac,0,LA_0069
    data/processed/fake/train_LA_T_002.flac,1,LA_0069

IMPORTANT:
    You must run scripts/prepare_dataset.py BEFORE this script.
    That script reads the official ASVspoof protocol files and writes
    data/splits/speaker_manifest.csv with real speaker IDs (e.g. LA_0069).
    If the manifest is absent, this script raises a RuntimeError rather than
    falling back to pseudo-speaker IDs.
"""

import sys
import random
from pathlib import Path
from collections import defaultdict

import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg
from preprocessing.audio_preprocessor import preprocess
from preprocessing.feature_extractor import get_mel_spectrogram


# ─────────────────────────────────────────────────────────────────────────────
# Speaker-aware split
# ─────────────────────────────────────────────────────────────────────────────

def create_splits_from_official_partitions(
    splits_dir: Path = cfg.SPLITS_DIR,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Assign train/val/test rows from speaker_manifest.csv using the OFFICIAL
    ASVspoof 2019 LA partition prefixes embedded in each filename:

        train_*  →  train.csv   (model training)
        dev_*    →  val.csv     (validation + threshold selection)
        eval_*   →  test.csv    (final unseen evaluation)

    Why prefer this over create_splits_random()?
    - It matches the standard ASVspoof benchmark.
    - ASVspoof partitions are already speaker-disjoint, so the
      speaker-independence guarantee holds automatically.
    - Judges can directly compare your results against published numbers.

    Raises:
        RuntimeError  — if speaker_manifest.csv is missing.
        RuntimeError  — if none of the rows match train_/dev_/eval_ prefixes
                         (falls through to create_splits_random in that case).

    Returns:
        (train_df, val_df, test_df)
    """
    df = _load_and_validate_manifest(splits_dir)

    fname = df["path"].apply(lambda p: Path(p).name)
    train_df = df[fname.str.startswith("train_")].reset_index(drop=True)
    val_df   = df[fname.str.startswith("dev_")  ].reset_index(drop=True)
    test_df  = df[fname.str.startswith("eval_") ].reset_index(drop=True)

    if train_df.empty and val_df.empty and test_df.empty:
        print(
            "  ⚠  No train_/dev_/eval_ prefixes found in manifest.\n"
            "     Falling back to random speaker split (create_splits_random)."
        )
        return create_splits_random(splits_dir=splits_dir)

    # ── Save ───────────────────────────────────────────────────────────
    splits_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(splits_dir / "train.csv", index=False)
    val_df.to_csv(splits_dir / "val.csv",   index=False)
    test_df.to_csv(splits_dir / "test.csv",  index=False)

    # ── Report ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("OFFICIAL ASVspoof PARTITION SPLIT")
    print("=" * 60)
    for name, part_df, prefix in [
        ("Train (train_*)", train_df, "train_"),
        ("Val   (dev_*  )", val_df,   "dev_"),
        ("Test  (eval_* )", test_df,  "eval_"),
    ]:
        real = (part_df["label"] == 0).sum()
        fake = (part_df["label"] == 1).sum()
        spk  = part_df["speaker_id"].nunique()
        print(f"  {name}: {len(part_df):>6} files  (real={real}, fake={fake}, speakers={spk})")

    # Verify speaker disjointness
    train_spk = set(train_df["speaker_id"])
    val_spk   = set(val_df["speaker_id"])
    test_spk  = set(test_df["speaker_id"])
    assert train_spk.isdisjoint(val_spk),  "Speaker leakage: train ∩ val"
    assert train_spk.isdisjoint(test_spk), "Speaker leakage: train ∩ test"
    assert val_spk.isdisjoint(test_spk),   "Speaker leakage: val ∩ test"
    print("  ✓ No speaker leakage between splits (official ASVspoof partitions)")
    print("=" * 60 + "\n")

    return train_df, val_df, test_df


def create_splits_random(
    splits_dir: Path = cfg.SPLITS_DIR,
    train_ratio: float = cfg.TRAIN_RATIO,
    val_ratio: float = cfg.VAL_RATIO,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create speaker-independent train/val/test splits by randomly assigning
    speakers 70/15/15 from speaker_manifest.csv.

    Use this only for datasets that do NOT have official train/dev/eval
    partitions (e.g. custom TTS recordings added in Stage 2).
    For ASVspoof 2019 LA, prefer create_splits_from_official_partitions().

    Raises:
        RuntimeError — if speaker_manifest.csv does not exist.

    Returns:
        (train_df, val_df, test_df)
    """
    df = _load_and_validate_manifest(splits_dir)
    random.seed(seed)

    # ── Group by speaker ──────────────────────────────────────────────────
    speakers = sorted(df["speaker_id"].unique().tolist())
    random.shuffle(speakers)

    n_train = max(1, int(len(speakers) * train_ratio))
    n_val   = max(1, int(len(speakers) * val_ratio))
    train_speakers = set(speakers[:n_train])
    val_speakers   = set(speakers[n_train: n_train + n_val])
    test_speakers  = set(speakers[n_train + n_val:])

    # ── Assign files ──────────────────────────────────────────────────────
    train_df = df[df["speaker_id"].isin(train_speakers)].reset_index(drop=True)
    val_df   = df[df["speaker_id"].isin(val_speakers)  ].reset_index(drop=True)
    test_df  = df[df["speaker_id"].isin(test_speakers) ].reset_index(drop=True)

    # ── Save ──────────────────────────────────────────────────────────────
    splits_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(splits_dir / "train.csv", index=False)
    val_df.to_csv(splits_dir / "val.csv",   index=False)
    test_df.to_csv(splits_dir / "test.csv",  index=False)

    # ── Report ────────────────────────────────────────────────────────────
    _print_split_report(train_df, val_df, test_df,
                        train_speakers, val_speakers, test_speakers)

    return train_df, val_df, test_df


def _load_and_validate_manifest(splits_dir: Path) -> pd.DataFrame:
    """
    Load speaker_manifest.csv and validate its content.
    Raises RuntimeError / ValueError on any problem.
    """
    manifest_path = splits_dir / "speaker_manifest.csv"
    if not manifest_path.exists():
        raise RuntimeError(
            f"Speaker manifest not found: {manifest_path}\n"
            "\n"
            "Run scripts/prepare_dataset.py first. That script reads the official\n"
            "ASVspoof 2019 LA protocol files and writes the manifest with real\n"
            "speaker IDs (e.g. LA_0069).\n"
            "\n"
            "Refusing to fall back to pseudo-speaker IDs because that would silently\n"
            "produce an invalid 'speaker-independent' split."
        )

    df = pd.read_csv(manifest_path)
    print(f"Loaded speaker manifest: {manifest_path} ({len(df)} rows)")

    required_cols = {"path", "label", "speaker_id"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"speaker_manifest.csv is missing columns: {missing_cols}\n"
            "Re-run scripts/prepare_dataset.py to regenerate it."
        )

    pseudo = df["speaker_id"].str.startswith("pseudo_spk_")
    if pseudo.any():
        raise ValueError(
            f"{pseudo.sum()} rows contain pseudo_spk_* IDs in the manifest.\n"
            "This indicates the manifest was generated with the old heuristic fallback.\n"
            "Delete data/splits/speaker_manifest.csv and re-run prepare_dataset.py."
        )

    if df.empty:
        raise ValueError(
            f"speaker_manifest.csv is empty: {manifest_path}\n"
            "Run scripts/prepare_dataset.py first."
        )

    return df


def _print_split_report(train_df, val_df, test_df,
                        train_spk, val_spk, test_spk) -> None:
    print("\n" + "=" * 55)
    print("SPEAKER-AWARE DATASET SPLIT")
    print("=" * 55)
    for name, df, spk in [("Train", train_df, train_spk),
                           ("Val  ", val_df, val_spk),
                           ("Test ", test_df, test_spk)]:
        real = (df["label"] == 0).sum()
        fake = (df["label"] == 1).sum()
        print(f"  {name}: {len(df):>5} files  "
              f"(real={real}, fake={fake}, speakers={len(spk)})")

    # Verify no speaker leakage
    assert train_spk.isdisjoint(val_spk), "Speaker leakage: train ∩ val"
    assert train_spk.isdisjoint(test_spk), "Speaker leakage: train ∩ test"
    assert val_spk.isdisjoint(test_spk), "Speaker leakage: val ∩ test"
    print("  ✓ No speaker leakage between splits")
    print("=" * 55 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# PyTorch Dataset
# ─────────────────────────────────────────────────────────────────────────────

class AudioDataset(Dataset):
    """
    Loads audio files from a split CSV and returns (mel_spectrogram, label).

    Args:
        csv_path  : path to train.csv / val.csv / test.csv
        augment   : apply training-time augmentation (Phase 2 only)
    """

    def __init__(self, csv_path: str | Path, augment: bool = False) -> None:
        self.df = pd.read_csv(csv_path)
        self.augment = augment

        # Fail loudly if any files are missing — silent zero-tensors corrupt training
        missing = [p for p in self.df["path"] if not Path(p).exists()]
        if missing:
            sample = missing[:5]
            raise RuntimeError(
                f"{len(missing)} audio file(s) listed in {csv_path} do not exist.\n"
                f"First missing files:\n"
                + "\n".join(f"  {p}" for p in sample)
                + (f"\n  ... and {len(missing) - 5} more" if len(missing) > 5 else "")
                + "\n\nRun scripts/prepare_dataset.py to rebuild the processed dataset."
            )

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.df.iloc[idx]
        path = row["path"]
        label = int(row["label"])   # 0=REAL, 1=AI_GENERATED

        # Fail loudly — never feed a zero-tensor silently into training.
        # If this raises, fix the dataset rather than masking the error.
        waveform = preprocess(path)              # (1, SAMPLES_PER_SEGMENT)
        if self.augment:
            waveform = _augment(waveform)
        mel = get_mel_spectrogram(waveform)      # (1, N_MELS, T)

        # Label as float tensor for BCEWithLogitsLoss
        target = torch.tensor(label, dtype=torch.float32)
        return mel, target


# ─────────────────────────────────────────────────────────────────────────────
# Training-time augmentation (Phase 2 — use AFTER baseline evaluation)
# ─────────────────────────────────────────────────────────────────────────────

def _augment(waveform: torch.Tensor) -> torch.Tensor:
    """
    Apply mild training-time augmentation.
    Only enabled when AudioDataset(augment=True).

    Augmentations applied randomly:
        - Gaussian noise addition
        - Random volume scaling
        - Small time shift

    DO NOT use at inference.
    """
    # Random volume gain (±3 dB)
    gain = 10 ** (random.uniform(-0.3, 0.3) / 20)
    waveform = waveform * gain

    # Gaussian noise (SNR ~30 dB equivalent)
    if random.random() < 0.5:
        noise = torch.randn_like(waveform) * 0.001
        waveform = waveform + noise

    # Small circular time shift (max 200ms)
    if random.random() < 0.3:
        shift = random.randint(0, int(cfg.SAMPLE_RATE * 0.2))
        waveform = torch.roll(waveform, shift, dims=1)

    # Re-normalize after augmentation
    peak = waveform.abs().max()
    if peak > 0:
        waveform = waveform / peak

    return waveform


# ─────────────────────────────────────────────────────────────────────────────
# DataLoader builders
# ─────────────────────────────────────────────────────────────────────────────

def get_dataloaders(
    train_csv: Path = cfg.TRAIN_CSV,
    val_csv: Path = cfg.VAL_CSV,
    test_csv: Path = cfg.TEST_CSV,
    batch_size: int = cfg.BATCH_SIZE,
    num_workers: int = cfg.NUM_WORKERS,
    augment_train: bool = False,  # set True in Phase 2 experiments
) -> tuple[DataLoader, DataLoader, DataLoader]:
    """
    Build and return (train_loader, val_loader, test_loader).
    """
    train_ds = AudioDataset(train_csv, augment=augment_train)
    val_ds = AudioDataset(val_csv, augment=False)
    test_ds = AudioDataset(test_csv, augment=False)

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True, drop_last=True,
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True,
    )
    test_loader = DataLoader(
        test_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True,
    )

    print(f"DataLoaders ready:")
    print(f"  Train: {len(train_ds)} samples, {len(train_loader)} batches")
    print(f"  Val  : {len(val_ds)} samples, {len(val_loader)} batches")
    print(f"  Test : {len(test_ds)} samples, {len(test_loader)} batches")

    return train_loader, val_loader, test_loader


# ─────────────────────────────────────────────────────────────────────────────
# CLI — run split creation
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Creating dataset splits from speaker manifest …")
    print("Strategy: official ASVspoof train_/dev_/eval_ partitions")
    print("(Requires scripts/prepare_dataset.py to have been run first)")
    cfg.ensure_dirs()
    train_df, val_df, test_df = create_splits_from_official_partitions()
    print(f"Splits saved to {cfg.SPLITS_DIR}")
