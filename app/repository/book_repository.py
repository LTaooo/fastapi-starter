from sqlmodel import select

from core.mysql import Mysql
from app.dto.request.book_list_req import BookListReq
from app.model.book import Book


class BookRepository:
    @classmethod
    async def find(cls, ident: int) -> Book | None:
        async with Mysql().session() as session:
            return await session.get(Book, ident)
            # statement = select('*').select_from(text('book')).where(text(f'id = {ident}')).limit(1)
            # results = await session.execute(statement)
            # return results.first()

    @classmethod
    async def list(cls, req: BookListReq) -> list[Book]:
        async with Mysql().session() as session:
            sql = select(Book).offset(req.get_offset()).limit(req.limit)
            result = await session.execute(sql)
            return result.scalars().all()
