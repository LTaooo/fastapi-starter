from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from sqlalchemy import Select, func
from sqlmodel import SQLModel, select

from core.mysql.mysql import Mysql
from core.mysql.page_resource import PageResource

T = TypeVar('T', bound=SQLModel)


class BaseRepository(Generic[T], ABC):
    @classmethod
    @abstractmethod
    def _get_client(cls) -> Mysql:
        raise NotImplementedError

    @classmethod
    async def _for_page(cls, page: int, limit: int, sql: Select) -> PageResource[T]:
        async with cls._get_client().session() as session:
            total = await session.exec(select(func.count()).select_from(sql.subquery()))
            sql = sql.offset(page).limit(limit)
            result = await session.exec(sql)
            return PageResource(total=total.one(), data=list(result.all()), limit=limit, page=page)
