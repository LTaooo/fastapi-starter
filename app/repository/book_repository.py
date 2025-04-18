from sqlmodel import select

from app.dto.request.book_create_req import BookCreateReq
from core.mysql.base_repository import BaseRepository
from app.dto.request.book_list_req import BookListReq
from app.model.book import Book
from core.mysql.database.book.book_session import BookSession
from core.mysql.page_resource import PageResource

from core.util.datetime import DateTime


class BookRepository(BaseRepository[Book]):
    @classmethod
    async def find(cls, session: BookSession, ident: int) -> Book | None:
        return await session.get_session().get(Book, ident)

    @classmethod
    async def list(cls, session: BookSession, req: BookListReq) -> list[Book]:
        sql = select(Book).offset(req.get_offset()).limit(req.limit)
        result = await session.get_session().exec(sql)
        books = list(result.all())
        return books

    @classmethod
    async def create(cls, session: BookSession, req: BookCreateReq) -> Book:
        book = Book(name=req.name, created_at=DateTime.now(), updated_at=DateTime.now())
        session.get_session().add(book)
        await session.get_session().flush()
        return book

    @classmethod
    async def page_list(cls, session: BookSession, req: BookListReq) -> PageResource[Book]:
        sql = select(Book)
        return await cls._for_page(session, req.page, req.limit, sql)
