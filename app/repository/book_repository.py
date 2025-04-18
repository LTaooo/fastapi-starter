from sqlmodel import select

from app.dto.request.book_create_req import BookCreateReq
from core.mysql.base_repository import BaseRepository
from core.mysql.mysql import Mysql
from app.dto.request.book_list_req import BookListReq
from app.model.book import Book
from core.mysql.page_resource import PageResource
from sqlmodel.ext.asyncio.session import AsyncSession

from core.util.datetime import DateTime


class BookRepository(BaseRepository[Book]):
    @classmethod
    def _get_client(cls) -> Mysql:
        return Mysql()

    @classmethod
    async def find(cls, session: AsyncSession, ident: int) -> Book | None:
        return await session.get(Book, ident)

    @classmethod
    async def list(cls, session: AsyncSession, req: BookListReq) -> list[Book]:
        books: list[Book] = []
        sql = select(Book).offset(req.get_offset()).limit(req.limit)
        result = await session.exec(sql)
        books = list(result.all())
        return books

    @classmethod
    async def create(cls, session: AsyncSession, req: BookCreateReq) -> Book:
        book = Book(name=req.name, created_at=DateTime.now(), updated_at=DateTime.now())
        session.add(book)
        await session.flush()
        return book

    @classmethod
    async def page_list(cls, session: AsyncSession, req: BookListReq) -> PageResource[Book]:
        sql = select(Book)
        return await cls._for_page(session, req.page, req.limit, sql)
