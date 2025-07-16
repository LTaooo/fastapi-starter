from typing import Type

from sqlalchemy import Select
from sqlmodel import col, select

from app.repository.params.book_repository_param import BookFilter
from core.mysql.base_repository import BaseRepository
from app.model.book import Book


class BookRepository(BaseRepository[Book, BookFilter]):
    def _model_class(self) -> Type[Book]:
        return Book

    def filter_class(self) -> Type[BookFilter]:
        return BookFilter

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
