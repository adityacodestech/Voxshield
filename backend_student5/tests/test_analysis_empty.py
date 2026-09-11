from fastapi.testclient import TestClient

from backend_student5.app.main import app


client = TestClient(app)


def test_analyze_rejects_empty_audio():
    response = client.post(
        "/api/v1/analyze",
        files={
            "file": (
                "empty.ogg",
                b"",
                "audio/ogg",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Uploaded audio file is empty"
    }