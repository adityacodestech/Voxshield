"""
scripts/prepare_dataset.py — VoxShield Dataset Preparation
===========================================================
Converts the raw ASVspoof 2019 LA dataset into a flat processed structure:

    data/processed/
        real/   ← bonafide utterances
        fake/   ← spoof utterances

Usage:
    python scripts/prepare_dataset.py

The script reads the official ASVspoof 2019 LA protocol files (.txt),
identifies bonafide vs spoof utterances, and copies (or hard-links) the
audio files to data/processed/real/ and data/processed/fake/.

It also prints class balance and unique speaker counts so you can check
dataset health before training.

ASVspoof 2019 LA download instructions
---------------------------------------
1. Register at: https://www.asvspoof.org/index2019.html
2. Download:
       ASVspoof2019_LA_train.zip
       ASVspoof2019_LA_dev.zip
       ASVspoof2019_LA_eval.zip
       ASVspoof2019_LA_cm_protocols.zip
3. Extract all into:  data/raw/ASVspoof2019_LA/
"""

import csv
import os
import sys
import shutil
from pathlib import Path

# Allow running from repo root or scripts/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))

import config as cfg

# ─────────────────────────────────────────────────────────────────────────────
# Protocol file columns (ASVspoof 2019 LA format)
# ─────────────────────────────────────────────────────────────────────────────
# speaker_id  utterance_id  <dash>  attack_type  label
# Example bonafide row:  LA_0069  LA_T_1138215  -  -  bonafide
# Example spoof row:     LA_0069  LA_T_1271820  -  A17  spoof
COL_SPEAKER = 0
COL_UTTERANCE = 1
COL_LABEL = 4   # 'bonafide' or 'spoof'


# ─────────────────────────────────────────────────────────────────────────────
# Subset → (audio_dir, protocol_file) mapping
# ─────────────────────────────────────────────────────────────────────────────
SUBSETS = {
    "train": (
        cfg.ASVSPOOF_TRAIN_DIR,
        cfg.ASVSPOOF_PROTO_DIR / "ASVspoof2019.LA.cm.train.trn.txt",
    ),
    "dev": (
        cfg.ASVSPOOF_DEV_DIR,
        cfg.ASVSPOOF_PROTO_DIR / "ASVspoof2019.LA.cm.dev.trl.txt",
    ),
    "eval": (
        cfg.ASVSPOOF_EVAL_DIR,
        cfg.ASVSPOOF_PROTO_DIR / "ASVspoof2019.LA.cm.eval.trl.txt",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _copy_file(src: Path, dst: Path, use_hardlink: bool = True) -> None:
    """Copy src → dst, preferring hard-links to save disk space."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return  # already processed
    try:
        if use_hardlink:
            os.link(src, dst)
        else:
            shutil.copy2(src, dst)
    except OSError:
        # Hard-link may fail across drives — fall back to copy
        shutil.copy2(src, dst)


def _find_audio(audio_dir: Path, utterance_id: str) -> Path | None:
    """
    Look for utterance_id with common extensions.
    ASVspoof 2019 uses .flac; other datasets may use .wav.
    """
    for ext in (".flac", ".wav", ".mp3"):
        p = audio_dir / f"{utterance_id}{ext}"
        if p.exists():
            return p
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Main processing
# ─────────────────────────────────────────────────────────────────────────────

def process_subset(
    subset_name: str,
    audio_dir: Path,
    protocol_file: Path,
    stats: dict,
    manifest: list,
) -> None:
    """Read one protocol file and copy utterances to processed dirs."""
    if not protocol_file.exists():
        print(f"  [SKIP] Protocol file not found: {protocol_file}")
        return
    if not audio_dir.exists():
        print(f"  [SKIP] Audio directory not found: {audio_dir}")
        return

    print(f"\nProcessing subset: {subset_name}")
    print(f"  Protocol : {protocol_file}")
    print(f"  Audio dir: {audio_dir}")

    with open(protocol_file, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    for line in lines:
        parts = line.split()
        if len(parts) < 5:
            continue

        speaker_id = parts[COL_SPEAKER]
        utterance_id = parts[COL_UTTERANCE]
        label = parts[COL_LABEL]  # 'bonafide' or 'spoof'

        src = _find_audio(audio_dir, utterance_id)
        if src is None:
            stats["missing"] += 1
            continue

        if label == "bonafide":
            dst = cfg.REAL_DIR / f"{subset_name}_{src.name}"
            _copy_file(src, dst)
            stats["real"] += 1
            stats["real_speakers"].add(speaker_id)
            manifest.append({"path": str(dst), "label": 0, "speaker_id": speaker_id})
        elif label == "spoof":
            dst = cfg.FAKE_DIR / f"{subset_name}_{src.name}"
            _copy_file(src, dst)
            stats["fake"] += 1
            stats["fake_speakers"].add(speaker_id)
            manifest.append({"path": str(dst), "label": 1, "speaker_id": speaker_id})
        else:
            stats["unknown_label"] += 1

    print(f"  Done — real so far: {stats['real']}, fake so far: {stats['fake']}")


def write_manifest(manifest: list) -> Path:
    """
    Write speaker_manifest.csv to cfg.SPLITS_DIR.

    Columns: path, label, speaker_id

    This file is the authoritative source of processed-audio-path → real speaker ID
    mapping consumed by training/dataset.py for speaker-independent splitting.
    """
    cfg.SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = cfg.SPLITS_DIR / "speaker_manifest.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "label", "speaker_id"])
        writer.writeheader()
        writer.writerows(manifest)
    return manifest_path


def print_summary(stats: dict, manifest_path: Path | None = None) -> None:
    total = stats["real"] + stats["fake"]
    print("\n" + "=" * 60)
    print("DATASET PREPARATION SUMMARY")
    print("=" * 60)
    print(f"  Real (bonafide) files : {stats['real']:>6}")
    print(f"  Fake (spoof)    files : {stats['fake']:>6}")
    print(f"  Total                 : {total:>6}")
    if total > 0:
        print(f"  Real %                : {100*stats['real']/total:.1f}%")
        print(f"  Fake %                : {100*stats['fake']/total:.1f}%")
    print(f"  Unique real speakers  : {len(stats['real_speakers'])}")
    print(f"  Unique fake speakers  : {len(stats['fake_speakers'])}")
    print(f"  Missing audio files   : {stats['missing']}")
    if stats["unknown_label"]:
        print(f"  Unknown labels        : {stats['unknown_label']}")
    print("=" * 60)
    print(f"\n  Processed real dir : {cfg.REAL_DIR}")
    print(f"  Processed fake dir : {cfg.FAKE_DIR}")
    if manifest_path:
        print(f"  Speaker manifest   : {manifest_path}")

    if stats["real"] == 0 or stats["fake"] == 0:
        print("\n  ⚠  One class has zero files.")
        print("     Check that the raw dataset was extracted to:")
        print(f"     {cfg.ASVSPOOF_DIR}")
    elif stats["real"] / max(stats["fake"], 1) > 5 or stats["fake"] / max(stats["real"], 1) > 5:
        print("\n  ⚠  Severe class imbalance detected.")
        print("     Consider using weighted loss or oversampling.")
    else:
        print("\n  ✓  Class balance looks reasonable.")


def main() -> None:
    print("VoxShield — Dataset Preparation")
    print(f"Root: {cfg.ROOT_DIR}\n")

    # Create output dirs
    cfg.ensure_dirs()

    stats: dict = {
        "real": 0,
        "fake": 0,
        "missing": 0,
        "unknown_label": 0,
        "real_speakers": set(),
        "fake_speakers": set(),
    }
    manifest: list = []  # accumulates (path, label, speaker_id) rows

    for subset_name, (audio_dir, protocol_file) in SUBSETS.items():
        process_subset(subset_name, audio_dir, protocol_file, stats, manifest)

    manifest_path = None
    if manifest:
        manifest_path = write_manifest(manifest)
        print(f"\n  ✓ Speaker manifest written: {manifest_path}")
        print(f"    ({len(manifest)} rows, "
              f"{len(stats['real_speakers'] | stats['fake_speakers'])} unique speakers)")

    print_summary(stats, manifest_path)

    if stats["real"] == 0 and stats["fake"] == 0:
        print("\nNothing was processed.")
        print("Download ASVspoof 2019 LA and extract to:")
        print(f"  {cfg.ASVSPOOF_DIR}\n")
        print("Then re-run this script.")


if __name__ == "__main__":
    main()
