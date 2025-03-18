from abc import ABC, abstractmethod
from typing import Generic
from sqlalchemy import Select, func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.mysql.mysql import Mysql
from core.mysql.page_resource import PageResource
from app.types.types import SQL_MODEL_TYPE


class BaseRepository(Generic[SQL_MODEL_TYPE], ABC):
    @classmethod
    @abstractmethod
    def _get_client(cls) -> Mysql:
        raise NotImplementedError

    @classmethod
    def _get_session(cls) -> AsyncSession:
        return cls._get_client().session()

    @classmethod
    async def _for_page(cls, page: int, limit: int, sql: Select) -> PageResource[SQL_MODEL_TYPE]:
        async with cls._get_client().session() as session:
            total = await session.exec(select(func.count()).select_from(sql.subquery()))
            sql = sql.offset(page).limit(limit)
            result = await session.exec(sql)
            return PageResource(total=total.one(), data=list(result.all()), limit=limit, page=page)
