from core.status_enum import StatusEnum


async def test_get(client):
    response = await client.post('/api/book/get', json={'id': 1})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert response.json()['data'] is not None


async def test_list(client):
    response = await client.post('/api/book/list', json={'page': 1, 'limit': 1})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert isinstance(response.json()['data']['data'], list)
    assert response.json()['data']['total'] >= len(response.json()['data']['data'])
