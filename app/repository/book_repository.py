from sqlalchemy import Select
from sqlmodel import col, select

from app.dto.request.book_create_req import BookCreateReq
from app.repository.params.book_filter import BookFilter
from core.mysql.base_repository import BaseRepository
from app.model.book import Book
from core.mysql.database.app.app_session import AppSession
from core.mysql.page_resource import PageResource

from core.util.datetime import DateTime


class BookRepository(BaseRepository[Book]):
    async def find(self, session: AppSession, ident: int) -> Book | None:
        return await session.get_session().get(Book, ident)

    async def list(self, session: AppSession, param: BookFilter) -> list[Book]:
        sql = self._filter(param)
        result = await session.get_session().execute(sql)
        return [Book.model_validate(row) for row in result]

    async def create(self, session: AppSession, req: BookCreateReq) -> Book:
        book = Book(name=req.name, created_at=DateTime.now(), updated_at=DateTime.now())
        session.get_session().add(book)
        await session.get_session().flush()
        return book

    async def page_list(self, session: AppSession, param: BookFilter) -> PageResource[Book]:
        sql = self._filter(param)
        return await self._for_page(session, param.page or 1, param.limit or 20, sql)

    def _filter(self, param: BookFilter) -> Select[tuple[Book]]:
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
