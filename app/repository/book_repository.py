from typing import Type

from sqlalchemy import Select
from sqlmodel import col

from app.repository.params.book_repository_param import BookFilter
from core.mysql.base_repository import BaseRepository
from app.model.book import Book


class BookRepository(BaseRepository[Book, BookFilter]):
    def _model_class(self) -> Type[Book]:
        return Book

    def filter_class(self) -> Type[BookFilter]:
        return BookFilter

    async def _filter(self, sql: Select[tuple[Book]], param: BookFilter) -> Select[tuple[Book]]:
        """
        基本筛选
        """
        if param.ids is not None:
            sql = sql.where(col(Book.id).in_(param.ids))
        if param.name_like is not None:
            sql = sql.where(col(Book.name).like(f'%{param.name_like}%'))

        return sql
