"""
inference/detector.py — VoxShield
====================================
Production inference module.  This is the main deliverable for integration
with Student 2 (audio pipeline) and Student 5 (risk engine).

Public API:
    detect_voice(audio_path) → dict

Usage:
    from inference.detector import detect_voice

    result = detect_voice("speech_001.wav")
    print(result)
    # {
    #   "prediction": "AI_GENERATED",
    #   "ai_probability": 0.94,
    #   "genuine_probability": 0.06,
    #   "threshold": 0.60,
    #   "model_version": "voxshield-v1"
    # }

Integration contract:
    - Input : path to a .wav file (or any torchaudio-supported format)
    - Output: dict with exactly the keys above
    - The caller (Student 5 Risk Engine) MUST use ai_probability, not just prediction
"""

import sys
from pathlib import Path
from typing import Optional

import torch

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg
from preprocessing.audio_preprocessor import preprocess
from preprocessing.feature_extractor import get_mel_spectrogram


# ─────────────────────────────────────────────────────────────────────────────
# Model loader (singleton — loaded once, reused for every call)
# ─────────────────────────────────────────────────────────────────────────────

_model = None
_threshold: float = cfg.DEFAULT_THRESHOLD
_model_type: str = "cnn"
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load_model(
    checkpoint_path: Optional[Path] = None,
    device: Optional[torch.device] = None,
) -> None:
    """
    Load the best checkpoint into the module-level singleton.
    Called automatically on first detect_voice() call.
    """
    global _model, _threshold, _model_type, _device

    if device:
        _device = device

    if checkpoint_path is None:
        checkpoint_path = cfg.MODELS_DIR / cfg.BEST_MODEL_NAME

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"No trained model found at {checkpoint_path}.\n"
            "Run:  python training/train.py   first."
        )

    ckpt = torch.load(checkpoint_path, map_location=_device)
    _model_type = ckpt.get("model_type", "cnn")
    _threshold = ckpt.get("optimal_threshold", cfg.DEFAULT_THRESHOLD)

    if _model_type == "cnn":
        from models.baseline_cnn import BaselineCNN
        _model = BaselineCNN()
    elif _model_type == "pretrained":
        from models.pretrained_model import Wav2Vec2Detector
        _model = Wav2Vec2Detector(freeze_encoder=False)
    else:
        raise ValueError(f"Unknown model_type in checkpoint: {_model_type!r}")

    _model.load_state_dict(ckpt["model_state_dict"])
    _model.to(_device)
    _model.eval()

    print(f"[VoxShield] Model loaded: {_model_type}  |  "
          f"threshold={_threshold:.4f}  |  device={_device}")


# ─────────────────────────────────────────────────────────────────────────────
# Core detection function
# ─────────────────────────────────────────────────────────────────────────────

def detect_voice(
    audio_path: str | Path,
    checkpoint_path: Optional[Path] = None,
) -> dict:
    """
    Detect whether a speech audio file is genuine or AI-generated.

    This function is the ONLY interface that other modules should call.
    Do not call preprocessing or model forward passes directly.

    Processing pipeline:
        audio_path
            → preprocess()        [same config as training — guaranteed]
            → get_mel_spectrogram()
            → model.forward()     [raw logit]
            → sigmoid()           [AI probability]
            → threshold           [from validation set selection]
            → prediction label

    Args:
        audio_path     : path to audio file (.wav, .flac, .mp3 …)
        checkpoint_path: optional override for model checkpoint path

    Returns:
        dict with keys:
            prediction        : "REAL" | "AI_GENERATED"
            ai_probability    : float in [0, 1]  — probability of being synthetic
            genuine_probability: float in [0, 1]  — probability of being genuine
            threshold         : float — operating threshold used
            model_version     : str

    Raises:
        FileNotFoundError: if audio_path or checkpoint does not exist
        RuntimeError     : if model cannot process the audio
    """
    global _model

    # Lazy-load model on first call
    if _model is None:
        _load_model(checkpoint_path)

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # ── Preprocessing — MUST match training exactly ───────────────────────
    try:
        waveform = preprocess(audio_path)           # (1, SAMPLES_PER_SEGMENT)
    except Exception as e:
        raise RuntimeError(f"Preprocessing failed for {audio_path}: {e}") from e

    # ── Feature extraction ────────────────────────────────────────────────
    mel = get_mel_spectrogram(waveform)             # (1, N_MELS, T)
    mel = mel.unsqueeze(0).to(_device)              # (1, 1, N_MELS, T) — add batch dim

    # ── Inference ─────────────────────────────────────────────────────────
    with torch.no_grad():
        logit = _model(mel)                         # (1, 1) raw logit
        ai_prob = torch.sigmoid(logit).item()       # float in [0, 1]

    genuine_prob = 1.0 - ai_prob
    prediction = "AI_GENERATED" if ai_prob >= _threshold else "REAL"

    return {
        "prediction": prediction,
        "ai_probability": round(ai_prob, 4),
        "genuine_probability": round(genuine_prob, 4),
        "threshold": round(_threshold, 4),
        "model_version": cfg.MODEL_VERSION,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Batch detection (for processing multiple segments efficiently)
# ─────────────────────────────────────────────────────────────────────────────

def detect_batch(
    audio_paths: list[str | Path],
    checkpoint_path: Optional[Path] = None,
) -> list[dict]:
    """
    Run detection on a list of audio files.

    More efficient than calling detect_voice() in a loop because it
    batches the model forward pass.

    Args:
        audio_paths: list of paths to audio files

    Returns:
        list of result dicts (same format as detect_voice())
    """
    global _model

    if _model is None:
        _load_model(checkpoint_path)

    results = []
    mels = []
    valid_indices = []

    for i, path in enumerate(audio_paths):
        try:
            waveform = preprocess(path)
            mel = get_mel_spectrogram(waveform)
            mels.append(mel)
            valid_indices.append(i)
        except Exception as e:
            results.append({
                "prediction": "ERROR",
                "ai_probability": -1.0,
                "genuine_probability": -1.0,
                "threshold": _threshold,
                "model_version": cfg.MODEL_VERSION,
                "error": str(e),
            })

    if mels:
        batch = torch.stack(mels).to(_device)   # (B, 1, N_MELS, T)
        with torch.no_grad():
            logits = _model(batch)              # (B, 1)
            probs = torch.sigmoid(logits).squeeze(1).cpu().numpy()

        for j, prob in zip(valid_indices, probs):
            ai_prob = float(prob)
            genuine_prob = 1.0 - ai_prob
            prediction = "AI_GENERATED" if ai_prob >= _threshold else "REAL"
            results.insert(j, {
                "prediction": prediction,
                "ai_probability": round(ai_prob, 4),
                "genuine_probability": round(genuine_prob, 4),
                "threshold": round(_threshold, 4),
                "model_version": cfg.MODEL_VERSION,
            })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Model reload (call if you want to swap checkpoints at runtime)
# ─────────────────────────────────────────────────────────────────────────────

def reload_model(checkpoint_path: Path, device: Optional[torch.device] = None) -> None:
    """Force reload the model from a new checkpoint path."""
    global _model
    _model = None
    _load_model(checkpoint_path, device)


# ─────────────────────────────────────────────────────────────────────────────
# CLI quick test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python inference/detector.py <audio_file> [audio_file2 ...]")
        sys.exit(1)

    for audio_file in sys.argv[1:]:
        print(f"\nDetecting: {audio_file}")
        try:
            result = detect_voice(audio_file)
            print(json.dumps(result, indent=2))
        except FileNotFoundError as e:
            print(f"  Error: {e}")
