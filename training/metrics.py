"""
training/metrics.py — VoxShield
=================================
All evaluation metrics for the binary fake-voice classifier.

Metrics:
    - Accuracy
    - Precision, Recall, F1 (macro and binary)
    - ROC-AUC
    - Equal Error Rate (EER)
    - Confusion Matrix
    - Threshold selection on validation set

Usage:
    from training.metrics import evaluate_predictions, select_threshold

    results = evaluate_predictions(y_true, y_scores, threshold=0.5)
    optimal_t = select_threshold(y_true_val, y_scores_val)
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay,
)

sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────────────────────
# Result container
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EvaluationResult:
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    roc_auc: float = 0.0
    eer: float = 0.0
    threshold: float = 0.5
    confusion: np.ndarray = field(default_factory=lambda: np.zeros((2, 2)))

    def __str__(self) -> str:
        return (
            f"\n{'─'*40}\n"
            f"  Accuracy  : {self.accuracy*100:.2f}%\n"
            f"  Precision : {self.precision*100:.2f}%\n"
            f"  Recall    : {self.recall*100:.2f}%\n"
            f"  F1        : {self.f1*100:.2f}%\n"
            f"  ROC-AUC   : {self.roc_auc*100:.2f}%\n"
            f"  EER       : {self.eer*100:.2f}%\n"
            f"  Threshold : {self.threshold:.4f}\n"
            f"{'─'*40}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Equal Error Rate
# ─────────────────────────────────────────────────────────────────────────────

def compute_eer(y_true: np.ndarray, y_scores: np.ndarray) -> float:
    """
    Compute Equal Error Rate (EER).

    EER is the point where False Acceptance Rate = False Rejection Rate.
    Lower EER = better detector.

    Args:
        y_true  : binary labels (0=REAL, 1=AI_GENERATED)
        y_scores: predicted AI probabilities in [0, 1]

    Returns:
        eer: float in [0, 1]
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    fnr = 1.0 - tpr   # False Negative Rate = 1 - True Positive Rate

    # EER is where FPR ≈ FNR
    diff = np.abs(fpr - fnr)
    eer_idx = np.argmin(diff)
    eer = (fpr[eer_idx] + fnr[eer_idx]) / 2.0
    return float(eer)


# ─────────────────────────────────────────────────────────────────────────────
# Threshold selection
# ─────────────────────────────────────────────────────────────────────────────

def select_threshold(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    metric: str = "f1",
    thresholds: np.ndarray | None = None,
) -> float:
    """
    Find the operating threshold that maximises a chosen metric on the
    validation set.

    Args:
        y_true    : binary labels
        y_scores  : predicted AI probabilities in [0, 1]
        metric    : 'f1' | 'recall' | 'precision'  (default: 'f1')
        thresholds: candidate thresholds (default: 0.05 to 0.95, step 0.05)

    Returns:
        optimal threshold (float)

    IMPORTANT: Run this on VALIDATION data only.
               Apply the returned threshold to TEST data without re-tuning.
    """
    if thresholds is None:
        thresholds = np.arange(0.05, 0.96, 0.05)

    best_score = -1.0
    best_t = 0.5

    for t in thresholds:
        y_pred = (y_scores >= t).astype(int)
        if metric == "f1":
            score = f1_score(y_true, y_pred, zero_division=0)
        elif metric == "recall":
            score = recall_score(y_true, y_pred, zero_division=0)
        elif metric == "precision":
            score = precision_score(y_true, y_pred, zero_division=0)
        else:
            raise ValueError(f"Unknown metric: {metric}")

        if score > best_score:
            best_score = score
            best_t = float(t)

    print(f"Threshold selection ({metric}): best_t={best_t:.2f}, "
          f"best_{metric}={best_score:.4f}")
    return best_t


# ─────────────────────────────────────────────────────────────────────────────
# Full evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_predictions(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    threshold: float = 0.5,
) -> EvaluationResult:
    """
    Compute all evaluation metrics.

    Args:
        y_true    : ground-truth binary labels (0=REAL, 1=AI_GENERATED)
        y_scores  : predicted AI probabilities in [0, 1]
        threshold : operating threshold (select on val set, apply to test)

    Returns:
        EvaluationResult dataclass
    """
    y_pred = (y_scores >= threshold).astype(int)

    result = EvaluationResult(
        accuracy=accuracy_score(y_true, y_pred),
        precision=precision_score(y_true, y_pred, zero_division=0),
        recall=recall_score(y_true, y_pred, zero_division=0),
        f1=f1_score(y_true, y_pred, zero_division=0),
        roc_auc=roc_auc_score(y_true, y_scores),
        eer=compute_eer(y_true, y_scores),
        threshold=threshold,
        confusion=confusion_matrix(y_true, y_pred),
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Plot helpers
# ─────────────────────────────────────────────────────────────────────────────

def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    save_path: str | Path | None = None,
    title: str = "Confusion Matrix",
) -> None:
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=["REAL", "AI_GENERATED"])
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, colorbar=True, cmap="Blues")
    ax.set_title(title)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"Confusion matrix saved to {save_path}")
    else:
        plt.show()
    plt.close(fig)


def plot_roc_curve(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    save_path: str | Path | None = None,
    title: str = "ROC Curve",
) -> None:
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    auc = roc_auc_score(y_true, y_scores)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(fpr, tpr, color="#4A90D9", lw=2, label=f"AUC = {auc:.4f}")
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"ROC curve saved to {save_path}")
    else:
        plt.show()
    plt.close(fig)


def plot_training_curves(
    train_losses: list[float],
    val_losses: list[float],
    train_accs: list[float],
    val_accs: list[float],
    save_path: str | Path | None = None,
) -> None:
    """Plot loss and accuracy curves from training."""
    epochs = range(1, len(train_losses) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(epochs, train_losses, label="Train Loss", color="#E05252")
    ax1.plot(epochs, val_losses, label="Val Loss", color="#4A90D9")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Training & Validation Loss")
    ax1.legend()

    ax2.plot(epochs, train_accs, label="Train Acc", color="#E05252")
    ax2.plot(epochs, val_accs, label="Val Acc", color="#4A90D9")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_title("Training & Validation Accuracy")
    ax2.legend()

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"Training curves saved to {save_path}")
    else:
        plt.show()
    plt.close(fig)
