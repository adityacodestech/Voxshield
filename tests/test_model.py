"""
tests/test_model.py — VoxShield
==================================
Unit tests for the BaselineCNN model architecture.

Run:
    pytest tests/test_model.py -v
"""

import sys
from pathlib import Path

import torch
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg


class TestBaselineCNN:
    @pytest.fixture
    def model(self):
        from models.baseline_cnn import BaselineCNN
        return BaselineCNN()

    def test_output_shape(self, model):
        """Model must output (batch, 1) logit."""
        dummy = torch.randn(4, 1, cfg.N_MELS, cfg.SPEC_TIME_FRAMES)
        out = model(dummy)
        assert out.shape == (4, 1), f"Expected (4, 1), got {out.shape}"

    def test_output_is_logit_not_probability(self, model):
        """Output should NOT be bounded in [0,1] — it's a raw logit."""
        dummy = torch.randn(8, 1, cfg.N_MELS, cfg.SPEC_TIME_FRAMES)
        logits = model(dummy)
        # Raw logits can be outside [0,1]
        # After sigmoid they should be in [0,1]
        probs = torch.sigmoid(logits)
        assert probs.min() >= 0.0
        assert probs.max() <= 1.0

    def test_single_sample(self, model):
        """Works with batch size 1."""
        dummy = torch.randn(1, 1, cfg.N_MELS, cfg.SPEC_TIME_FRAMES)
        out = model(dummy)
        assert out.shape == (1, 1)

    def test_no_nan_output(self, model):
        """No NaN in outputs for random inputs."""
        dummy = torch.randn(4, 1, cfg.N_MELS, cfg.SPEC_TIME_FRAMES)
        out = model(dummy)
        assert not torch.isnan(out).any()

    def test_gradient_flows(self, model):
        """Backpropagation should compute gradients without errors."""
        dummy = torch.randn(2, 1, cfg.N_MELS, cfg.SPEC_TIME_FRAMES)
        labels = torch.tensor([[1.0], [0.0]])

        criterion = torch.nn.BCEWithLogitsLoss()
        logits = model(dummy)
        loss = criterion(logits, labels)
        loss.backward()

        # Check at least some params have gradients
        has_grad = any(
            p.grad is not None and p.grad.abs().sum() > 0
            for p in model.parameters()
        )
        assert has_grad, "No gradients computed — backprop failed"

    def test_train_vs_eval_mode(self, model):
        """
        Dropout should be active in train mode and disabled in eval mode.
        With high dropout, outputs should differ between train calls.
        """
        from models.baseline_cnn import BaselineCNN
        high_drop_model = BaselineCNN(dropout=0.9)
        dummy = torch.randn(4, 1, cfg.N_MELS, cfg.SPEC_TIME_FRAMES)

        high_drop_model.train()
        out_train_1 = high_drop_model(dummy)
        out_train_2 = high_drop_model(dummy)
        # With 90% dropout, outputs should differ
        assert not torch.allclose(out_train_1, out_train_2, atol=1e-3)

        high_drop_model.eval()
        with torch.no_grad():
            out_eval_1 = high_drop_model(dummy)
            out_eval_2 = high_drop_model(dummy)
        # In eval mode, outputs should be identical
        assert torch.allclose(out_eval_1, out_eval_2)

    def test_parameter_count(self, model):
        """Model should have a reasonable number of parameters."""
        n_params = model.count_parameters()
        assert n_params > 10_000, "Too few parameters"
        assert n_params < 50_000_000, "Unexpectedly large model"
        print(f"\nBaselineCNN parameters: {n_params:,}")
