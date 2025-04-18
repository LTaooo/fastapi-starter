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
    async def _for_page(cls, session: AsyncSession, page: int, limit: int, sql: Select) -> PageResource[SQL_MODEL_TYPE]:
        page_resource: PageResource[SQL_MODEL_TYPE] = PageResource(total=0, data=[], limit=limit, page=page)
        total = await session.exec(select(func.count()).select_from(sql.subquery()))
        sql = sql.offset(page).limit(limit)
        result = await session.exec(sql)  # type: ignore
        page_resource.total = total.one()
        page_resource.data = list(result.all())
        return page_resource
