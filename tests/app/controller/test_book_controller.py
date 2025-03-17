from unittest import TestCase
from fastapi.testclient import TestClient

from core.status_enum import StatusEnum
from main import app


class BookControllerTest(TestCase):
    client = TestClient(app)

    def test_get(self):
        response = self.client.post('/api/book/get', json={'id': 1})
        assert response.status_code == 200
        assert response.json()['code'] == StatusEnum.success.value
        assert response.json()['data'] is not None

    def test_list(self):
        response = self.client.post('/api/book/list', json={'page': 1, 'limit': 1})
        assert response.status_code == 200
        assert response.json()['code'] == StatusEnum.success.value
        assert isinstance(response.json()['data']['data'], list)
        assert response.json()['data']['total'] >= len(response.json()['data']['data'])
