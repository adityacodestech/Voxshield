from fastapi.testclient import TestClient

from backend_student5.app.main import app


client = TestClient(app)


def test_analyze_rejects_unsupported_format():
    response = client.post(
        "/api/v1/analyze",
        files={
            "file": (
                "test.txt",
                b"This is not an audio file",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported audio format: .txt"
    }
    