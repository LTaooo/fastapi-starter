from sqlalchemy import Select, select
from sqlmodel import col

from app.dto.request.book_create_req import BookCreateReq
from app.repository.params.book_filter import BookFilter
from core.mysql.base_repository import BaseRepository
from app.model.book import Book
from core.mysql.database.book.book_session import BookSession
from core.mysql.page_resource import PageResource

from core.util.datetime import DateTime


class BookRepository(BaseRepository[Book]):
    @classmethod
    async def find(cls, session: BookSession, ident: int) -> Book | None:
        return await session.get_session().get(Book, ident)

    @classmethod
    async def list(cls, session: BookSession, param: BookFilter) -> list[Book]:
        sql = cls._filter(param)
        result = await session.get_session().execute(sql)
        return [Book.model_validate(row) for row in result]

    @classmethod
    async def create(cls, session: BookSession, req: BookCreateReq) -> Book:
        book = Book(name=req.name, created_at=DateTime.now(), updated_at=DateTime.now())
        session.get_session().add(book)
        await session.get_session().flush()
        return book

    @classmethod
    async def page_list(cls, session: BookSession, param: BookFilter) -> PageResource[Book]:
        sql = cls._filter(param)
        return await cls._for_page(session, param.page or 1, param.limit or 20, sql)

    @classmethod
    def _filter(cls, param: BookFilter) -> Select[tuple[Book]]:
        """
        通用筛选
        :param param:
        :return:
        """
        sql = select(Book)
        if param.ids is not None:
            sql = sql.where(col(Book.id).in_(param.ids))
        if param.name is not None:
            sql = sql.where(col(Book.name).like(f'%{param.name}%'))
        if param.limit is not None:
            sql = sql.limit(param.limit)
        if param.page is not None:
            sql = sql.offset(param.page)
        return sql
