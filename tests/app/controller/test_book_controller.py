from httpx import AsyncClient

from app.dto.request.book_req import BookBulkUpdateNameReq
from app.model.book import Book
from app.repository.book_repository import BookRepository
from app.repository.params.book_repository_param import BookCreate, BookFilter
from core.mysql.database.app.app_session import AppSession
from core.status_enum import StatusEnum
from core.util.datetime import DateTime


def _book_name(prefix: str) -> str:
    return f'{prefix}{DateTime.datetime()}'


async def _create_book(session: AppSession, name: str) -> Book:
    repository = BookRepository()
    async with session.transaction():
        return await repository.create(session, BookCreate(name=name))


async def test_get_book(client: AsyncClient, app_session: AppSession):
    book = await _create_book(app_session, _book_name('test-get'))
    response = await client.get('/api/book/get', params={'book_id': book.id})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert response.json()['data']['name'] == book.name


async def test_list_book(client: AsyncClient, app_session: AppSession):
    await _create_book(app_session, _book_name('test-list'))
    response = await client.post('/api/book/list', json={'page': 1, 'limit': 1})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value
    assert isinstance(response.json()['data']['data'], list)
    assert response.json()['data']['total'] >= 1


async def test_book_repository_create(app_session: AppSession):
    repository = BookRepository()
    async with app_session.transaction():
        book1 = await repository.create(app_session, BookCreate(name=_book_name('test-create')))
        book2 = await repository.create(app_session, BookCreate(name=_book_name('test-create')))
    assert book2.id > book1.id

    updated_name = _book_name('test-update')
    async with app_session.transaction():
        book1.name = _book_name('test-update-1')
    async with app_session.transaction():
        updated = await repository.update(app_session, book1, {'name': updated_name})
    assert updated.name == updated_name


async def test_book_repository_query(app_session: AppSession):
    repository = BookRepository()
    await _create_book(app_session, _book_name('test-query'))
    book_filter = BookFilter(name_like='test-query')
    book_filter.order_by(Book.created_at.desc())
    book = await repository.get_one(app_session, book_filter)
    assert isinstance(book, Book)


async def test_bulk_update_name(client: AsyncClient, app_session: AppSession):
    book1 = await _create_book(app_session, _book_name('test-bulk'))
    book2 = await _create_book(app_session, _book_name('test-bulk'))
    name1 = f'{_book_name("test-bulk-new")}-{book1.id}'
    name2 = f'{_book_name("test-bulk-new")}-{book2.id}'
    param = [
        BookBulkUpdateNameReq(id=book1.id, name=name1).model_dump(),
        BookBulkUpdateNameReq(id=book2.id, name=name2).model_dump(),
    ]
    response = await client.post('/api/book/bulk_update_name', json={'books': param})
    assert response.status_code == 200
    assert response.json()['code'] == StatusEnum.success.value

    for book_id, name in ((book1.id, name1), (book2.id, name2)):
        detail = await client.get('/api/book/get', params={'book_id': book_id})
        assert detail.json()['data']['name'] == name
