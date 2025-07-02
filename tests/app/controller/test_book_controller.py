from httpx import AsyncClient

from app.repository.book_repository import BookRepository
from app.repository.params.book_repository_param import BookCreate
from core.mysql.database.app.app_database import AppDatabase
from core.mysql.database.app.app_session import AppSession
from core.status_enum import StatusEnum


async def test_get(client: AsyncClient):
    response = await client.post('/api/book/get', json={'id': 1})
    print(response.json())
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert response.json()['data'] is not None


async def test_list(client: AsyncClient):
    response = await client.post('/api/book/list', json={'page': 1, 'limit': 1})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert isinstance(response.json()['data']['data'], list)
    assert response.json()['data']['total'] >= len(response.json()['data']['data'])


async def test_book_repository_create(client: AsyncClient):
    repository = BookRepository()
    session: AppSession
    async with AppDatabase.with_session() as session:
        async with session.get_session().begin():
            book1 = await repository.create(session, BookCreate(name='test'))
            book2 = await repository.create(session, BookCreate(name='test'))
            await session.get_session().commit()
            assert book2.id - book1.id == 1
