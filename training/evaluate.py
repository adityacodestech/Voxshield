"""
training/evaluate.py — VoxShield
==================================
Final evaluation on the held-out test set.

Run AFTER training is complete:
    python training/evaluate.py

This script:
  1. Loads the best saved checkpoint (voxshield_best.pth)
  2. Reads the optimal threshold saved during training
  3. Runs inference on the test split
  4. Prints: Accuracy, Precision, Recall, F1, ROC-AUC, EER
  5. Saves: confusion matrix plot, ROC curve plot

IMPORTANT:
  - This uses the threshold from the VALIDATION set (saved in checkpoint).
  - Do NOT re-tune the threshold on the test set.
  - Document the achieved numbers honestly — do not re-run until you hit
    a desired score.
"""

import sys
from pathlib import Path

import torch
import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg
from training.dataset import AudioDataset
from training.metrics import (
    evaluate_predictions, select_threshold,
    plot_confusion_matrix, plot_roc_curve,
    EvaluationResult,
)
from torch.utils.data import DataLoader

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(checkpoint_path: Path):
    """Load model and threshold from saved checkpoint."""
    ckpt = torch.load(checkpoint_path, map_location=DEVICE)
    model_type = ckpt.get("model_type", "cnn")

    if model_type == "cnn":
        from models.baseline_cnn import BaselineCNN
        model = BaselineCNN()
    elif model_type == "pretrained":
        from models.pretrained_model import Wav2Vec2Detector
        model = Wav2Vec2Detector(freeze_encoder=False)
    else:
        raise ValueError(f"Unknown model_type in checkpoint: {model_type}")

    model.load_state_dict(ckpt["model_state_dict"])
    model.to(DEVICE)
    model.eval()

    threshold = ckpt.get("optimal_threshold", cfg.DEFAULT_THRESHOLD)
    epoch = ckpt.get("epoch", "?")
    val_f1 = ckpt.get("val_f1", 0.0)

    print(f"Loaded checkpoint: {checkpoint_path.name}")
    print(f"  Trained epochs   : {epoch}")
    print(f"  Validation F1    : {val_f1:.4f}")
    print(f"  Optimal threshold: {threshold:.4f}  (from val set)")
    return model, threshold


@torch.no_grad()
def run_inference_on_loader(model, loader) -> tuple[np.ndarray, np.ndarray]:
    """Collect all ground-truth labels and predicted probabilities."""
    all_labels = []
    all_scores = []

    for batch_mel, batch_label in tqdm(loader, desc="  Evaluating"):
        batch_mel = batch_mel.to(DEVICE)
        logits = model(batch_mel)
        probs = torch.sigmoid(logits).squeeze(1).cpu().numpy()
        labels = batch_label.numpy()

        all_labels.extend(labels.tolist())
        all_scores.extend(probs.tolist())

    return np.array(all_labels), np.array(all_scores)


def evaluate(
    checkpoint_path: Path = cfg.MODELS_DIR / cfg.BEST_MODEL_NAME,
    test_csv: Path = cfg.TEST_CSV,
    output_dir: Path = cfg.MODELS_DIR,
) -> EvaluationResult:
    """
    Full test-set evaluation pipeline.

    Args:
        checkpoint_path: path to saved best model .pth
        test_csv       : path to test split CSV
        output_dir     : where to save plots

    Returns:
        EvaluationResult
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load ──────────────────────────────────────────────────────────────
    if not checkpoint_path.exists():
        print(f"No checkpoint found at {checkpoint_path}")
        print("Run:  python training/train.py   first.")
        return None

    model, threshold = load_model(checkpoint_path)

    if not test_csv.exists():
        print(f"No test CSV found at {test_csv}")
        print("Run:  python training/dataset.py   first.")
        return None

    test_ds = AudioDataset(test_csv, augment=False)
    test_loader = DataLoader(
        test_ds, batch_size=cfg.BATCH_SIZE,
        shuffle=False, num_workers=cfg.NUM_WORKERS,
    )

    print(f"\nEvaluating on {len(test_ds)} test samples …\n")

    # ── Inference ─────────────────────────────────────────────────────────
    y_true, y_scores = run_inference_on_loader(model, test_loader)

    # ── Compute metrics ───────────────────────────────────────────────────
    result = evaluate_predictions(y_true, y_scores, threshold=threshold)

    # ── Print ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("TEST SET EVALUATION — VoxShield Voice Detector")
    print("=" * 50)
    print(result)

    # ── Plots ─────────────────────────────────────────────────────────────
    y_pred = (y_scores >= threshold).astype(int)

    plot_confusion_matrix(
        y_true, y_pred,
        save_path=output_dir / "confusion_matrix.png",
        title="VoxShield — Confusion Matrix (Test Set)",
    )
    plot_roc_curve(
        y_true, y_scores,
        save_path=output_dir / "roc_curve.png",
        title="VoxShield — ROC Curve (Test Set)",
    )

    # ── Save text report ──────────────────────────────────────────────────
    report_path = output_dir / "evaluation_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("VoxShield Voice Detector — Test Set Evaluation\n")
        f.write("=" * 50 + "\n")
        f.write(f"Checkpoint : {checkpoint_path}\n")
        f.write(f"Test CSV   : {test_csv}\n")
        f.write(f"Samples    : {len(test_ds)}\n")
        f.write(str(result) + "\n")
        f.write("\nConfusion Matrix:\n")
        f.write(str(result.confusion) + "\n")

    print(f"\nReport saved to: {report_path}")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Robustness testing helper
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_robustness(
    audio_files: list[str],
    ground_truth: list[int],
    noise_level: float = 0.01,
    checkpoint_path: Path = cfg.MODELS_DIR / cfg.BEST_MODEL_NAME,
) -> None:
    """
    Test detector on manually specified audio files under various conditions.

    Args:
        audio_files  : list of paths to audio files
        ground_truth : list of labels (0=REAL, 1=AI_GENERATED)
        noise_level  : std dev of added Gaussian noise
        checkpoint_path: model checkpoint to use
    """
    from preprocessing.audio_preprocessor import preprocess
    from preprocessing.feature_extractor import get_mel_spectrogram

    model, threshold = load_model(checkpoint_path)
    model.eval()

    print("\n── Robustness Test ──────────────────────────────────")
    print(f"{'File':<30} {'True':>6} {'Pred':>14} {'Prob':>6}")
    print("─" * 60)

    with torch.no_grad():
        for path, label in zip(audio_files, ground_truth):
            try:
                wav = preprocess(path)

                # Add noise
                if noise_level > 0:
                    wav = wav + torch.randn_like(wav) * noise_level
                    wav = wav / (wav.abs().max() + 1e-9)

                mel = get_mel_spectrogram(wav).unsqueeze(0).to(DEVICE)
                logit = model(mel)
                prob = torch.sigmoid(logit).item()
                pred = "AI_GEN" if prob >= threshold else "REAL"
                true_str = "AI_GEN" if label == 1 else "REAL"
                match = "✓" if (prob >= threshold) == label else "✗"

                print(f"{Path(path).name:<30} {true_str:>6} → {pred:>10}  "
                      f"{prob:.3f}  {match}")
            except Exception as e:
                print(f"{Path(path).name:<30} ERROR: {e}")

    print("─" * 60)


if __name__ == "__main__":
    evaluate()
