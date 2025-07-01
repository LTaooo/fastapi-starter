from typing import Type

from pydantic import Field
from sqlalchemy import Select
from sqlmodel import col, select

from app.dto.request.book_req import BookCreateReq
from core.mysql.base_filter import BaseFilter
from core.mysql.base_repository import BaseRepository
from app.model.book import Book
from core.mysql.database.app.app_session import AppSession

from core.util.datetime import DateTime


class BookFilter(BaseFilter):
    ids: list[int] | None = Field(default=None, description='书籍id')
    name: str | None = Field(default=None, description='书名')


class BookRepository(BaseRepository[Book, BookFilter]):
    def _model_class(self) -> Type[Book]:
        return Book

    def filter_class(self) -> Type[BookFilter]:
        return BookFilter

    async def create(self, session: AppSession, req: BookCreateReq) -> Book:
        book = Book(name=req.name, created_at=DateTime.now(), updated_at=DateTime.now())
        return await self.save(session, book, False)

    def _filter(self, param: BookFilter) -> Select[tuple[Book]]:
        """
        通用筛选
        :param param:
        :return:
        """
        sql = select(Book)
        if param.ids is not None:
            sql = sql.where(col('id').in_(param.ids))
        if param.name is not None:
            sql = sql.where(col('name').like(f'%{param.name}%'))
        if param.limit is not None:
            sql = sql.limit(param.limit)
        if param.page is not None:
            sql = sql.offset(param.page)
        return sql
