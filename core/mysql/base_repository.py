from abc import ABC, abstractmethod
from typing import Generic, Type

from pydantic import BaseModel
from sqlalchemy import Select, func
from sqlmodel import select

from core.exception.runtime_exception import RuntimeException
from core.mysql.base_mysql_session import BaseMysqlSession
from core.mysql.page_resource import PageResource
from core.types.types import SQL_MODEL_TYPE, FILTER_TYPE


class BaseRepository(Generic[SQL_MODEL_TYPE, FILTER_TYPE], ABC):
    @abstractmethod
    def _model_class(self) -> Type[SQL_MODEL_TYPE]:
        raise NotImplementedError

    @abstractmethod
    def filter_class(self) -> Type[FILTER_TYPE]:
        raise NotImplementedError

    async def find(self, session: BaseMysqlSession, pk: int) -> SQL_MODEL_TYPE | None:
        return await session.get_session().get(self._model_class(), pk)

    async def find_or_raise(self, session: BaseMysqlSession, pk: int, message: str | None = None) -> SQL_MODEL_TYPE:
        if not message:
            message = f'{pk} not found'
        model = await self.find(session, pk)
        if not model:
            raise RuntimeException(message)
        return model

    async def get_one(self, session: BaseMysqlSession, param: FILTER_TYPE) -> SQL_MODEL_TYPE | None:
        sql = self._filter(param)
        result = await session.get_session().exec(sql)  # type: ignore
        return result.first()

    async def list(self, session: BaseMysqlSession, param: FILTER_TYPE) -> list[SQL_MODEL_TYPE]:
        sql = self._filter(param)
        result = await session.get_session().exec(sql)  # type: ignore
        return list(result.all())

    async def page_list(self, session: BaseMysqlSession, param: FILTER_TYPE) -> PageResource[SQL_MODEL_TYPE]:
        sql = self._filter(param)
        return await self._for_page(session, param.page or 1, param.limit or 20, sql)

    async def save(self, session: BaseMysqlSession, model: SQL_MODEL_TYPE) -> SQL_MODEL_TYPE:
        session.get_session().add(model)
        await session.get_session().flush()
        return model

    async def _for_page(self, session: BaseMysqlSession, page: int, limit: int, sql: Select) -> PageResource[SQL_MODEL_TYPE]:
        page_resource: PageResource[SQL_MODEL_TYPE] = PageResource(total=0, data=[], limit=limit, page=page)
        total = await session.get_session().exec(select(func.count()).select_from(sql.subquery()))
        offset = (page - 1) * limit
        sql = sql.offset(offset).limit(limit)
        result = await session.get_session().exec(sql)  # type: ignore
        page_resource.total = total.one()
        page_resource.data = list(result.all())
        return page_resource

    async def delete_by_id(self, session: BaseMysqlSession, pk: int) -> None:
        model = await self.find(session, pk)
        if not model:
            raise ValueError(f'Model with id {pk} not found')
        await session.get_session().delete(model)

    async def delete(self, session: BaseMysqlSession, model: SQL_MODEL_TYPE) -> None:
        await session.get_session().delete(model)

    @abstractmethod
    def _filter(self, param: BaseModel) -> Select[tuple[SQL_MODEL_TYPE]]:
        """
        通用筛选
        :param param:
        :return:
        """
        raise NotImplementedError
