"""
models/pretrained_model.py — VoxShield Phase 2
================================================
Transfer-learning based fake-voice detector using wav2vec2-base as an
audio encoder.

Architecture:
    Input  : (batch, SAMPLES_PER_SEGMENT)  — raw 16 kHz mono waveform
    Encoder: wav2vec2-base (frozen initially)
    Head   : Linear(768→256) → ReLU → Dropout → Linear(256→1)
    Output : (batch, 1)  — raw logit (NOT sigmoid)

Usage:
    Phase 1  — Train BaselineCNN first and establish a performance baseline.
    Phase 2  — Install transformers:
                   pip install transformers accelerate
               Then run:
                   python training/train.py --model pretrained

NOTE:
    This module requires `transformers` to be installed.
    It is commented out of requirements.txt by default.
    Install manually:  pip install transformers accelerate
"""

import sys
from pathlib import Path

import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg

try:
    from transformers import Wav2Vec2Model, Wav2Vec2Config
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Classification head (shared by all pretrained encoder approaches)
# ─────────────────────────────────────────────────────────────────────────────

class ClassificationHead(nn.Module):
    """
    MLP head attached to a frozen/fine-tuned audio encoder.

    Args:
        encoder_dim: output dimension of the encoder (768 for wav2vec2-base)
        hidden_dim : intermediate dense layer size
        dropout    : dropout probability
    """

    def __init__(self, encoder_dim: int = 768, hidden_dim: int = 256,
                 dropout: float = cfg.DROPOUT) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(encoder_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),   # raw logit — NO sigmoid
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ─────────────────────────────────────────────────────────────────────────────
# Wav2Vec2 — fake voice detector
# ─────────────────────────────────────────────────────────────────────────────

class Wav2Vec2Detector(nn.Module):
    """
    Fake-voice detector built on top of wav2vec2-base.

    Training strategy (two phases):
        Phase A — freeze encoder, train head only (faster, lower memory)
        Phase B — unfreeze top N transformer layers for fine-tuning

    Args:
        model_name  : HuggingFace model identifier
        freeze_encoder: whether to freeze the encoder (True = Phase A)
        hidden_dim  : head hidden layer size
        dropout     : dropout probability
    """

    MODEL_NAME = "facebook/wav2vec2-base"
    ENCODER_DIM = 768   # wav2vec2-base last hidden state dimension

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        freeze_encoder: bool = True,
        hidden_dim: int = 256,
        dropout: float = cfg.DROPOUT,
    ) -> None:
        super().__init__()

        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers is not installed. Run:\n"
                "    pip install transformers accelerate\n"
                "Then retry importing Wav2Vec2Detector."
            )

        print(f"Loading pretrained encoder: {model_name}")
        self.encoder = Wav2Vec2Model.from_pretrained(model_name)
        self.head = ClassificationHead(self.ENCODER_DIM, hidden_dim, dropout)

        if freeze_encoder:
            self.freeze_encoder()

    # ── Encoder freeze / unfreeze ──────────────────────────────────────────

    def freeze_encoder(self) -> None:
        """Phase A: freeze all encoder weights."""
        for param in self.encoder.parameters():
            param.requires_grad = False
        print("Encoder frozen — training head only.")

    def unfreeze_top_layers(self, n: int = 4) -> None:
        """
        Phase B: unfreeze the top N transformer layers for fine-tuning.
        Call this after Phase A head training has converged.

        Args:
            n: number of top transformer layers to unfreeze
        """
        # Unfreeze feature projection and top N encoder layers
        for param in self.encoder.feature_projection.parameters():
            param.requires_grad = True

        layers = self.encoder.encoder.layers
        for layer in layers[-n:]:
            for param in layer.parameters():
                param.requires_grad = True

        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"Unfroze top {n} transformer layers — "
              f"trainable params: {trainable:,}")

    # ── Forward ────────────────────────────────────────────────────────────

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        """
        Args:
            waveform: (batch, SAMPLES_PER_SEGMENT)
                      — raw 16 kHz mono waveform (NOT Mel spectrogram)

        Returns:
            logit: (batch, 1)  — raw logit
        """
        # Wav2Vec2 expects (batch, sequence_length) with no channel dim
        if waveform.dim() == 3:
            waveform = waveform.squeeze(1)   # (batch, 1, T) → (batch, T)

        outputs = self.encoder(input_values=waveform)
        # last_hidden_state: (batch, time_steps, 768)
        # Mean-pool over time to get a fixed-size representation
        pooled = outputs.last_hidden_state.mean(dim=1)   # (batch, 768)
        logit = self.head(pooled)                         # (batch, 1)
        return logit

    def count_parameters(self) -> dict:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total": total, "trainable": trainable}


# ─────────────────────────────────────────────────────────────────────────────
# Quick sanity check
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not TRANSFORMERS_AVAILABLE:
        print("transformers not installed. Run: pip install transformers accelerate")
        sys.exit(1)

    model = Wav2Vec2Detector(freeze_encoder=True)
    params = model.count_parameters()
    print(f"Total params    : {params['total']:,}")
    print(f"Trainable params: {params['trainable']:,}")

    # Simulate a batch of 2 raw waveforms
    dummy = torch.randn(2, cfg.SAMPLES_PER_SEGMENT)
    logits = model(dummy)
    probs = torch.sigmoid(logits)

    print(f"Input shape  : {dummy.shape}")
    print(f"Logit shape  : {logits.shape}")
    print(f"Sample probs : {probs.squeeze().detach().tolist()}")
    print("✓ Forward pass successful")
