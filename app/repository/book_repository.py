from sqlmodel import select

from core.mysql.base_repository import BaseRepository
from core.mysql.mysql import Mysql
from app.dto.request.book_list_req import BookListReq
from app.model.book import Book
from core.mysql.page_resource import PageResource


class BookRepository(BaseRepository[Book]):
    @classmethod
    def _get_client(cls) -> Mysql:
        return Mysql()

    @classmethod
    async def find(cls, ident: int) -> Book | None:
        async with cls._get_client().session() as session:
            return await session.get(Book, ident)

    @classmethod
    async def list(cls, req: BookListReq) -> list[Book]:
        async with cls._get_client().session() as session:
            sql = select(Book).offset(req.get_offset()).limit(req.limit)
            result = await session.exec(sql)
            return list(result.all())

    @classmethod
    async def page_list(cls, req: BookListReq) -> PageResource[Book]:
        sql = select(Book)
        return await cls._for_page(req.page, req.limit, sql)
