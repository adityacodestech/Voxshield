"""
tests/test_inference.py — VoxShield
======================================
Integration tests for the detect_voice() inference function.

These tests mock the model so they run without a trained checkpoint.

Run:
    pytest tests/test_inference.py -v
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import torch
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_sine_wav(path: Path, duration: float = 3.0) -> None:
    import soundfile as sf
    t = np.linspace(0, duration, int(16000 * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * 440.0 * t)
    sf.write(str(path), wave, 16000)


def _mock_model(ai_prob: float = 0.94):
    """Create a mock model that returns a fixed logit."""
    model = MagicMock()
    # sigmoid(logit) = ai_prob → logit = log(ai_prob / (1 - ai_prob))
    logit_val = float(np.log(ai_prob / (1.0 - ai_prob + 1e-9)))
    model.return_value = torch.tensor([[logit_val]])
    model.eval = MagicMock(return_value=None)
    return model


# ─────────────────────────────────────────────────────────────────────────────
# Response schema validation
# ─────────────────────────────────────────────────────────────────────────────

REQUIRED_KEYS = {
    "prediction", "ai_probability", "genuine_probability",
    "threshold", "model_version",
}

def _validate_response(result: dict) -> None:
    assert isinstance(result, dict)
    assert REQUIRED_KEYS.issubset(result.keys()), (
        f"Missing keys: {REQUIRED_KEYS - result.keys()}"
    )
    assert result["prediction"] in ("REAL", "AI_GENERATED")
    assert 0.0 <= result["ai_probability"] <= 1.0
    assert 0.0 <= result["genuine_probability"] <= 1.0
    assert abs(result["ai_probability"] + result["genuine_probability"] - 1.0) < 1e-3
    assert isinstance(result["threshold"], float)
    assert isinstance(result["model_version"], str)


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectVoiceSchema:
    """Verify the output JSON contract."""

    def test_ai_generated_response_schema(self, tmp_path):
        """A high-probability fake should return AI_GENERATED with correct schema."""
        import inference.detector as det

        wav = tmp_path / "fake.wav"
        _make_sine_wav(wav)

        # Inject mock model with high AI probability (0.94)
        det._model = _mock_model(ai_prob=0.94)
        det._threshold = 0.5
        det._device = torch.device("cpu")

        result = det.detect_voice(wav)
        _validate_response(result)
        assert result["prediction"] == "AI_GENERATED"
        assert result["ai_probability"] > 0.5

    def test_real_response_schema(self, tmp_path):
        """A low-probability fake should return REAL with correct schema."""
        import inference.detector as det

        wav = tmp_path / "real.wav"
        _make_sine_wav(wav)

        det._model = _mock_model(ai_prob=0.06)
        det._threshold = 0.5
        det._device = torch.device("cpu")

        result = det.detect_voice(wav)
        _validate_response(result)
        assert result["prediction"] == "REAL"
        assert result["genuine_probability"] > 0.5

    def test_probabilities_sum_to_one(self, tmp_path):
        import inference.detector as det

        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        det._model = _mock_model(ai_prob=0.73)
        det._threshold = 0.5
        det._device = torch.device("cpu")

        result = det.detect_voice(wav)
        total = result["ai_probability"] + result["genuine_probability"]
        assert abs(total - 1.0) < 1e-3

    def test_missing_file_raises(self):
        import inference.detector as det
        det._model = _mock_model()
        det._threshold = 0.5

        with pytest.raises(FileNotFoundError):
            det.detect_voice("/nonexistent/audio.wav")


class TestThresholdBehaviour:
    """Verify threshold is applied correctly."""

    def test_probability_above_threshold_is_fake(self, tmp_path):
        import inference.detector as det

        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        det._model = _mock_model(ai_prob=0.75)
        det._threshold = 0.60   # 0.75 >= 0.60 → AI_GENERATED
        det._device = torch.device("cpu")

        result = det.detect_voice(wav)
        assert result["prediction"] == "AI_GENERATED"

    def test_probability_below_threshold_is_real(self, tmp_path):
        import inference.detector as det

        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        det._model = _mock_model(ai_prob=0.55)
        det._threshold = 0.60   # 0.55 < 0.60 → REAL
        det._device = torch.device("cpu")

        result = det.detect_voice(wav)
        assert result["prediction"] == "REAL"

    def test_threshold_included_in_response(self, tmp_path):
        import inference.detector as det

        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        det._model = _mock_model(ai_prob=0.5)
        det._threshold = 0.65
        det._device = torch.device("cpu")

        result = det.detect_voice(wav)
        assert abs(result["threshold"] - 0.65) < 1e-3


class TestModelVersion:
    def test_version_string_in_response(self, tmp_path):
        import inference.detector as det

        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        det._model = _mock_model()
        det._threshold = 0.5
        det._device = torch.device("cpu")

        result = det.detect_voice(wav)
        assert result["model_version"] == cfg.MODEL_VERSION


class TestAPIEndpoint:
    """Integration tests for the FastAPI endpoint."""

    @pytest.fixture
    def client(self):
        """Create a FastAPI test client with a mock model."""
        import inference.detector as det
        det._model = _mock_model(ai_prob=0.94)
        det._threshold = 0.5
        det._device = torch.device("cpu")

        # Patch model_ready in the API module
        with patch("api.detector_api._model_ready", True):
            from fastapi.testclient import TestClient
            from api.detector_api import app
            yield TestClient(app)

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_model_info_endpoint(self, client):
        response = client.get("/model-info")
        assert response.status_code == 200
        data = response.json()
        assert "sample_rate" in data
        assert data["sample_rate"] == cfg.SAMPLE_RATE

    def test_detect_voice_endpoint(self, client, tmp_path):
        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        with open(wav, "rb") as f:
            response = client.post(
                "/detect-voice",
                files={"file": ("test.wav", f, "audio/wav")},
            )

        assert response.status_code == 200
        data = response.json()
        _validate_response(data)

    def test_invalid_file_type_rejected(self, client):
        response = client.post(
            "/detect-voice",
            files={"file": ("script.py", b"print('hello')", "text/plain")},
        )
        assert response.status_code == 400
