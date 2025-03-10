from fastapi.testclient import TestClient

from core.status_enum import StatusEnum
from main import app

client = TestClient(app)


def test_get_book():
    response = client.post("/book/get", json={"id": 1})
    assert response.status_code == 200
    assert response.json()["code"] == StatusEnum.success.value
    assert response.json()["data"] is not None

def test_list_book():
    response = client.post("/book/list", json={"page": 1, "limit": 1})
    assert response.status_code == 200
    assert response.json()["code"] == StatusEnum.success.value
    assert isinstance(response.json()["data"]["data"], list)
    assert response.json()["data"]["total"] >= len(response.json()["data"]["data"])
