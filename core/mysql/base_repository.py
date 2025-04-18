from abc import ABC
from typing import Generic
from sqlalchemy import Select, func
from sqlmodel import select

from core.mysql.base_mysql_session import BaseMysqlSession
from core.mysql.page_resource import PageResource
from app.types.types import SQL_MODEL_TYPE


class BaseRepository(Generic[SQL_MODEL_TYPE], ABC):
    @classmethod
    async def _for_page(cls, session: BaseMysqlSession, page: int, limit: int, sql: Select) -> PageResource[SQL_MODEL_TYPE]:
        page_resource: PageResource[SQL_MODEL_TYPE] = PageResource(total=0, data=[], limit=limit, page=page)
        total = await session.get_session().exec(select(func.count()).select_from(sql.subquery()))
        sql = sql.offset(page).limit(limit)
        result = await session.get_session().exec(sql)  # type: ignore
        page_resource.total = total.one()
        page_resource.data = list(result.all())
        return page_resource
