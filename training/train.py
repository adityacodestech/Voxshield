"""
training/train.py — VoxShield
================================
Training loop for the BaselineCNN (and optionally the pretrained model).

Usage:
    # Baseline CNN (Phase 1)
    python training/train.py

    # With pretrained model (Phase 2 — requires transformers)
    python training/train.py --model pretrained

Features:
    - BCEWithLogitsLoss  (numerically stable, no sigmoid in model)
    - Adam optimizer + ReduceLROnPlateau scheduler
    - Per-epoch: train loss, val loss, train acc, val acc
    - Best checkpoint saved by validation F1
    - Early stopping after N epochs without improvement
    - Threshold selection on validation set at end of training
"""

import sys
import argparse
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg
from training.dataset import get_dataloaders, create_splits_from_official_partitions
from training.metrics import (
    evaluate_predictions, select_threshold,
    plot_training_curves, EvaluationResult,
)


# ─────────────────────────────────────────────────────────────────────────────
# Device
# ─────────────────────────────────────────────────────────────────────────────

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def print_device_info() -> None:
    print(f"Device : {DEVICE}")
    if DEVICE.type == "cuda":
        print(f"GPU    : {torch.cuda.get_device_name(0)}")
        mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"VRAM   : {mem:.1f} GB")
    else:
        print("Running on CPU — training will be slow. Consider Google Colab.")


# ─────────────────────────────────────────────────────────────────────────────
# One epoch helpers
# ─────────────────────────────────────────────────────────────────────────────

def train_one_epoch(
    model: nn.Module,
    loader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
) -> tuple[float, float]:
    """
    Run one training epoch.

    Returns:
        (avg_loss, accuracy)
    """
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for batch_mel, batch_label in tqdm(loader, desc="  Train", leave=False):
        batch_mel = batch_mel.to(DEVICE)
        batch_label = batch_label.to(DEVICE).unsqueeze(1)  # (B, 1)

        optimizer.zero_grad()
        logits = model(batch_mel)                    # (B, 1) raw logit
        loss = criterion(logits, batch_label)
        loss.backward()

        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()

        total_loss += loss.item() * len(batch_label)

        # Accuracy (threshold = 0.5 during training, refined later on val)
        preds = (torch.sigmoid(logits) >= 0.5).squeeze(1).long()
        targets = batch_label.squeeze(1).long()
        correct += (preds == targets).sum().item()
        total += len(targets)

    return total_loss / total, correct / total


@torch.no_grad()
def validate_one_epoch(
    model: nn.Module,
    loader,
    criterion: nn.Module,
) -> tuple[float, float, np.ndarray, np.ndarray]:
    """
    Run one validation epoch.

    Returns:
        (avg_loss, accuracy, all_labels, all_scores)
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    all_labels = []
    all_scores = []

    for batch_mel, batch_label in tqdm(loader, desc="  Val  ", leave=False):
        batch_mel = batch_mel.to(DEVICE)
        batch_label = batch_label.to(DEVICE).unsqueeze(1)

        logits = model(batch_mel)
        loss = criterion(logits, batch_label)
        total_loss += loss.item() * len(batch_label)

        probs = torch.sigmoid(logits).squeeze(1)
        preds = (probs >= 0.5).long()
        targets = batch_label.squeeze(1).long()

        correct += (preds == targets).sum().item()
        total += len(targets)

        all_labels.extend(targets.cpu().numpy().tolist())
        all_scores.extend(probs.cpu().numpy().tolist())

    return (
        total_loss / total,
        correct / total,
        np.array(all_labels),
        np.array(all_scores),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main training loop
# ─────────────────────────────────────────────────────────────────────────────

def train(
    model_type: str = "cnn",
    augment: bool = False,
    epochs: int = cfg.NUM_EPOCHS,
    batch_size: int = cfg.BATCH_SIZE,
    lr: float = cfg.LEARNING_RATE,
    early_stop_patience: int = 10,
) -> nn.Module:
    """
    Full training loop.

    Args:
        model_type : 'cnn' | 'pretrained'
        augment    : enable training-time augmentation (Phase 2)
        epochs     : max training epochs
        batch_size : mini-batch size
        lr         : initial learning rate
        early_stop_patience: stop after this many epochs with no val F1 improvement

    Returns:
        best model (loaded from checkpoint)
    """
    print_device_info()
    cfg.ensure_dirs()

    # ── Data ──────────────────────────────────────────────────────────────
    if not cfg.TRAIN_CSV.exists():
        print("No splits found — creating dataset splits …")
        create_splits_from_official_partitions()

    train_loader, val_loader, _ = get_dataloaders(
        batch_size=batch_size, augment_train=augment
    )

    # ── Model ─────────────────────────────────────────────────────────────
    if model_type == "cnn":
        from models.baseline_cnn import BaselineCNN
        model = BaselineCNN().to(DEVICE)
        checkpoint_path = cfg.MODELS_DIR / cfg.CHECKPOINT_NAME
        print(f"\nModel : BaselineCNN  "
              f"({model.count_parameters():,} trainable params)")
    elif model_type == "pretrained":
        from models.pretrained_model import Wav2Vec2Detector
        model = Wav2Vec2Detector(freeze_encoder=True).to(DEVICE)
        checkpoint_path = cfg.MODELS_DIR / "voxshield_pretrained_v1.pth"
        params = model.count_parameters()
        print(f"\nModel : Wav2Vec2Detector  "
              f"({params['trainable']:,} trainable / {params['total']:,} total params)")
    else:
        raise ValueError(f"Unknown model_type: {model_type!r}")

    # ── Loss / Optimizer / Scheduler ──────────────────────────────────────
    # BCEWithLogitsLoss — numerically stable; model outputs raw logit
    criterion = nn.BCEWithLogitsLoss()
    optimizer = Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr,
        weight_decay=cfg.WEIGHT_DECAY,
    )
    scheduler = ReduceLROnPlateau(optimizer, mode="max", factor=0.5,
                                  patience=5)

    # ── History ───────────────────────────────────────────────────────────
    history = {
        "train_loss": [], "val_loss": [],
        "train_acc": [], "val_acc": [],
    }
    best_val_f1 = 0.0
    no_improve = 0

    print(f"\nTraining for up to {epochs} epochs …\n")

    for epoch in range(1, epochs + 1):
        t0 = time.time()

        # ── Train ──────────────────────────────────────────────────────────
        train_loss, train_acc = train_one_epoch(model, train_loader,
                                                 optimizer, criterion)

        # ── Validate ───────────────────────────────────────────────────────
        val_loss, val_acc, val_labels, val_scores = validate_one_epoch(
            model, val_loader, criterion
        )

        # Find the optimal threshold for this epoch, then measure F1 at that
        # threshold.  This ensures checkpoint selection uses the same operating
        # procedure as deployment (not a fixed 0.5 cutoff).
        epoch_threshold = select_threshold(val_labels, val_scores, metric="f1")
        val_result = evaluate_predictions(val_labels, val_scores,
                                          threshold=epoch_threshold)
        val_f1 = val_result.f1

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        elapsed = time.time() - t0
        print(
            f"Epoch {epoch:3d}/{epochs}  "
            f"| train_loss={train_loss:.4f}  train_acc={train_acc*100:.1f}%  "
            f"| val_loss={val_loss:.4f}  val_acc={val_acc*100:.1f}%  "
            f"| val_F1={val_f1:.4f} (t={epoch_threshold:.2f})  "
            f"| {elapsed:.1f}s"
        )

        scheduler.step(val_f1)

        # ── Checkpoint ─────────────────────────────────────────────────────
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            no_improve = 0
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_f1": val_f1,
                "val_acc": val_acc,
                "model_type": model_type,
            }, checkpoint_path)
            print(f"  ✓ New best model saved (val_F1={val_f1:.4f})")
        else:
            no_improve += 1
            if no_improve >= early_stop_patience:
                print(f"\nEarly stopping at epoch {epoch} "
                      f"(no improvement for {early_stop_patience} epochs)")
                break

    # ── Post-training: threshold selection on full validation set ─────────
    print("\nRunning threshold selection on validation set …")
    model.load_state_dict(
        torch.load(checkpoint_path, map_location=DEVICE)["model_state_dict"]
    )
    _, _, val_labels, val_scores = validate_one_epoch(model, val_loader, criterion)
    optimal_threshold = select_threshold(val_labels, val_scores, metric="f1")

    print(f"\nOptimal threshold : {optimal_threshold:.4f}")
    print("Threshold saved in checkpoint — detector.py loads it automatically.\n")

    # ── Save best model with threshold ─────────────────────────────────────
    best_path = cfg.MODELS_DIR / cfg.BEST_MODEL_NAME
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    checkpoint["optimal_threshold"] = optimal_threshold
    torch.save(checkpoint, best_path)
    print(f"Best model with threshold saved to: {best_path}")

    # ── Training curves ────────────────────────────────────────────────────
    curves_path = cfg.MODELS_DIR / "training_curves.png"
    plot_training_curves(
        history["train_loss"], history["val_loss"],
        history["train_acc"], history["val_acc"],
        save_path=curves_path,
    )

    return model


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def _parse_args():
    parser = argparse.ArgumentParser(description="VoxShield model training")
    parser.add_argument("--model", choices=["cnn", "pretrained"], default="cnn",
                        help="Model architecture to train (default: cnn)")
    parser.add_argument("--augment", action="store_true",
                        help="Enable training-time augmentation (Phase 2)")
    parser.add_argument("--epochs", type=int, default=cfg.NUM_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=cfg.BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=cfg.LEARNING_RATE)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    train(
        model_type=args.model,
        augment=args.augment,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )
