from abc import ABC, abstractmethod
from typing import AsyncGenerator, Generic
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
    async def _get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        async for session in cls._get_client().session():
            yield session

    @classmethod
    async def _for_page(cls, page: int, limit: int, sql: Select) -> PageResource[SQL_MODEL_TYPE]:
        page_resource: PageResource[SQL_MODEL_TYPE] = PageResource(total=0, data=[], limit=limit, page=page)
        async for session in cls._get_session():
            total = await session.exec(select(func.count()).select_from(sql.subquery()))
            sql = sql.offset(page).limit(limit)
            result = await session.exec(sql)  # type: ignore
            page_resource.total = total.one()
            page_resource.data = list(result.all())
        return page_resource
