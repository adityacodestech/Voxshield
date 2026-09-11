from fastapi.testclient import TestClient

from backend_student5.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "AI Voice Security API"
    }