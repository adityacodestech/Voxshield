"""
models/baseline_cnn.py — VoxShield
====================================
Simple CNN for binary classification of Mel spectrograms.

Architecture:
    Input  : (batch, 1, N_MELS, T)   — log-Mel spectrogram
    Output : (batch, 1)               — raw logit (NOT sigmoid)

IMPORTANT:
    The model outputs a RAW LOGIT, not a probability.
    - During training : BCEWithLogitsLoss(logit, target)  — numerically stable
    - During inference: prob = torch.sigmoid(logit)       — applied in detector.py

    Do NOT add a Sigmoid layer inside this class.
"""

import sys
from pathlib import Path

import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg


class ConvBlock(nn.Module):
    """Conv2D → BatchNorm → ReLU → MaxPool"""

    def __init__(self, in_channels: int, out_channels: int,
                 kernel_size: int = 3, pool_size: int = 2) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size,
                      padding=kernel_size // 2, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=pool_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class BaselineCNN(nn.Module):
    """
    3-block CNN for binary fake-voice detection.

    Input shape : (batch, 1, N_MELS, T)
    Output shape: (batch, 1)  — raw logit

    Args:
        n_mels    : number of Mel frequency bins (default: cfg.N_MELS)
        channels  : out-channels list for each conv block (default: cfg.CNN_CHANNELS)
        hidden_dim: fully-connected hidden layer size (default: cfg.CNN_HIDDEN_DIM)
        dropout   : dropout probability (default: cfg.DROPOUT)
    """

    def __init__(
        self,
        n_mels: int = cfg.N_MELS,
        channels: list[int] = None,
        hidden_dim: int = cfg.CNN_HIDDEN_DIM,
        dropout: float = cfg.DROPOUT,
    ) -> None:
        super().__init__()

        if channels is None:
            channels = cfg.CNN_CHANNELS  # e.g. [32, 64, 128]

        # ── Convolutional backbone ────────────────────────────────────────────
        in_ch = 1
        conv_blocks = []
        for out_ch in channels:
            conv_blocks.append(ConvBlock(in_ch, out_ch))
            in_ch = out_ch
        self.backbone = nn.Sequential(*conv_blocks)

        # ── Global Average Pooling → collapses (freq, time) to a vector ──────
        self.gap = nn.AdaptiveAvgPool2d(1)  # → (batch, channels[-1], 1, 1)

        # ── Classifier ────────────────────────────────────────────────────────
        self.classifier = nn.Sequential(
            nn.Flatten(),                             # (batch, channels[-1])
            nn.Linear(channels[-1], hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),                 # raw logit
            # NO Sigmoid here — applied at inference only
        )

        self._init_weights()

    def _init_weights(self) -> None:
        """Kaiming init for conv layers, Xavier for linear."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out",
                                        nonlinearity="relu")
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, 1, N_MELS, T)

        Returns:
            logit: (batch, 1)  — use sigmoid at inference; BCEWithLogitsLoss in training
        """
        x = self.backbone(x)   # (batch, C, h, w)
        x = self.gap(x)        # (batch, C, 1, 1)
        x = self.classifier(x) # (batch, 1)
        return x

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ─────────────────────────────────────────────────────────────────────────────
# Quick sanity check
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    model = BaselineCNN()
    print(f"BaselineCNN — trainable parameters: {model.count_parameters():,}")

    # Simulate a batch of 4 Mel spectrograms
    dummy_input = torch.randn(4, 1, cfg.N_MELS, cfg.SPEC_TIME_FRAMES)
    logits = model(dummy_input)
    probs = torch.sigmoid(logits)

    print(f"Input shape  : {dummy_input.shape}")
    print(f"Logit shape  : {logits.shape}")
    print(f"Prob shape   : {probs.shape}")
    print(f"Sample probs : {probs.squeeze().detach().tolist()}")
    print("✓ Forward pass successful")
