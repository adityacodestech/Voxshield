from fastapi.testclient import TestClient

from backend_student5.app.main import app


class FakePipeline:
    def process_frame(self, data):
        return {
            "audio": b"\x00" * 640,
            "duration": 0.30,
            "reason": "test",
        }


def fake_create_pipeline():
    return FakePipeline()


def fake_detect_voice(audio_path):
    return {
        "prediction": "AI_GENERATED",
        "ai_probability": 0.94,
        "genuine_probability": 0.06,
        "threshold": 0.60,
        "model_version": "voxshield-v1",
    }


def test_audio_websocket_integration(monkeypatch):

    import backend_student5.app.routes.audio as audio_route

    monkeypatch.setattr(
        audio_route,
        "create_audio_pipeline",
        fake_create_pipeline,
    )

    monkeypatch.setattr(
        audio_route,
        "detect_voice",
        fake_detect_voice,
    )

    client = TestClient(app)

    with client.websocket_connect("/ws/audio") as websocket:

        connected = websocket.receive_json()

        assert connected["status"] == "connected"

        websocket.send_bytes(b"\x00" * 640)

        result = websocket.receive_json()

        assert result["status"] == "analyzed"

        assert result["detection"]["prediction"] == "AI_GENERATED"

        assert result["detection"]["ai_probability"] == 0.94

        assert "risk" in result

        assert result["risk"]["risk_score"] is not None