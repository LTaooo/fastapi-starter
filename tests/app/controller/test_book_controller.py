from httpx import AsyncClient

from app.dto.request.book_req import BookBulkUpdateNameReq
from app.model.book import Book
from app.repository.book_repository import BookRepository
from app.repository.params.book_repository_param import BookCreate, BookFilter
from core.mysql.database.app.app_session import AppSession
from core.status_enum import StatusEnum
from core.util.datetime import DateTime


def _unique(prefix: str) -> str:
    return f'{prefix}-{DateTime.millisecond()}'


async def _create_book(client: AsyncClient, name: str) -> int:
    response = await client.post('/api/book/create', json={'name': name})
    assert response.status_code == 200
    body = response.json()
    assert body['code'] == StatusEnum.success.value
    return body['data']['id']


async def test_get_book(client: AsyncClient):
    book_id = await _create_book(client, _unique('get'))
    response = await client.get('/api/book/get', params={'book_id': book_id})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert response.json()['data']['id'] == book_id


async def test_list_book(client: AsyncClient):
    name = _unique('list')
    book_id = await _create_book(client, name)
    response = await client.post('/api/book/list', json={'page': 1, 'limit': 1, 'name': name})
    assert response.status_code == 200
    body = response.json()
    assert body['code'] == StatusEnum.success.value
    assert body['data']['total'] == 1
    assert len(body['data']['data']) == 1
    assert body['data']['data'][0]['id'] == book_id


async def test_book_repository_create(app_session: AppSession):
    repository = BookRepository()
    book1 = await repository.create(app_session, BookCreate(name=_unique('repo')))
    book2 = await repository.create(app_session, BookCreate(name=_unique('repo')))
    assert book2.id - book1.id == 1

    await repository.update(app_session, book1, {'name': _unique('repo-updated')})


async def test_book_repository_query(app_session: AppSession):
    repository = BookRepository()
    prefix = _unique('query')
    await repository.create(app_session, BookCreate(name=f'{prefix}-a'))
    await repository.create(app_session, BookCreate(name=f'{prefix}-b'))

    book_filter = BookFilter(name_like=prefix)
    book_filter.order_by(Book.created_at.desc())
    book = await repository.get_one(app_session, book_filter)
    assert isinstance(book, Book)
    assert book.name.startswith(prefix)

    books = await repository.list(app_session, BookFilter(name_like=prefix))
    assert {book.name for book in books} == {f'{prefix}-a', f'{prefix}-b'}

    page = await repository.page_list(app_session, BookFilter(name_like=prefix, page=1, limit=1))
    assert page.total == 2
    assert len(page.data) == 1


async def test_bulk_update_name(client: AsyncClient):
    ids = [await _create_book(client, _unique('bulk')) for _ in range(2)]
    updated_prefix = _unique('bulk-updated')
    books = [
        BookBulkUpdateNameReq(id=book_id, name=f'{updated_prefix}-{index}').model_dump() for index, book_id in enumerate(ids)
    ]
    response = await client.post('/api/book/bulk_update_name', json={'books': books})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value

    for index, book_id in enumerate(ids):
        result = await client.get('/api/book/get', params={'book_id': book_id})
        assert result.json()['data']['name'] == f'{updated_prefix}-{index}'
