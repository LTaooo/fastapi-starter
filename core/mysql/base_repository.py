from abc import ABC, abstractmethod
from typing import Generic, Type

from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.runtime_exception import RuntimeException
from core.mysql.orm.auto_time import AutoTime
from core.mysql.page_resource import PageResource
from core.types.types import SQL_MODEL_TYPE, FILTER_TYPE


class BaseRepository(Generic[SQL_MODEL_TYPE, FILTER_TYPE], ABC):
    @abstractmethod
    def _model_class(self) -> Type[SQL_MODEL_TYPE]:
        raise NotImplementedError

    @abstractmethod
    def filter_class(self) -> Type[FILTER_TYPE]:
        raise NotImplementedError

    async def find(self, session: AsyncSession, pk: int) -> SQL_MODEL_TYPE | None:
        return await session.get(self._model_class(), pk)

    async def find_or_raise(self, session: AsyncSession, pk: int, message: str | None = None) -> SQL_MODEL_TYPE:
        if not message:
            message = f'{pk} not found'
        model = await self.find(session, pk)
        if not model:
            raise RuntimeException(message)
        return model

    async def get_one(self, session: AsyncSession, param: FILTER_TYPE) -> SQL_MODEL_TYPE | None:
        sql = self._common_filter(param)
        sql = sql.limit(1)
        result = await session.execute(sql)
        return result.scalar_one_or_none()

    async def update(self, session: AsyncSession, model: SQL_MODEL_TYPE, update_data: dict | BaseModel) -> SQL_MODEL_TYPE:
        model = await session.merge(model)
        if isinstance(update_data, BaseModel):
            update_data = update_data.model_dump()
        columns = {column.key for column in self._model_class().__table__.columns}
        primary_field = model.get_primary_field()
        for key, value in update_data.items():
            if key not in columns or key == primary_field:
                raise RuntimeException(f'Invalid update field: {key}')
            setattr(model, key, value)
        return await self.save(session, model)

    async def create(self, session: AsyncSession, param: BaseModel | dict) -> SQL_MODEL_TYPE:
        if isinstance(param, BaseModel):
            param = param.model_dump()
        model = self._model_class()(**param)
        return await self.save(session, model)

    def auto_set_timestamp(self, model: SQL_MODEL_TYPE) -> SQL_MODEL_TYPE:
        if isinstance(model, AutoTime):
            model.auto_set_time()
        return model

    async def list(self, session: AsyncSession, param: FILTER_TYPE) -> list[SQL_MODEL_TYPE]:
        sql = self._apply_page(self._common_filter(param), param)
        result = await session.execute(sql)
        return list(result.scalars().all())

    async def page_list(self, session: AsyncSession, param: FILTER_TYPE) -> PageResource[SQL_MODEL_TYPE]:
        sql = self._common_filter(param)
        if not param.order_bys:
            sql = sql.order_by(*self._model_class().__mapper__.primary_key)
        return await self._for_page(session, param.page or 1, param.limit or 20, sql)

    async def save(self, session: AsyncSession, model: SQL_MODEL_TYPE) -> SQL_MODEL_TYPE:
        self.auto_set_timestamp(model)
        if not model.get_primary_key():
            session.add(model)
        await session.flush()
        return model

    async def _for_page(self, session: AsyncSession, page: int, limit: int, sql: Select) -> PageResource[SQL_MODEL_TYPE]:
        page_resource = PageResource(total=0, data=[], limit=limit, page=page)

        count_sql = select(func.count()).select_from(sql.order_by(None).subquery())
        total_result = await session.execute(count_sql)
        page_resource.total = total_result.scalar_one()

        offset = (page - 1) * limit
        paginated_sql = sql.offset(offset).limit(limit)

        result = await session.execute(paginated_sql)
        page_resource.data = list(result.scalars().all())

        return page_resource

    async def delete_by_id(self, session: AsyncSession, pk: int) -> None:
        model = await self.find(session, pk)
        if not model:
            raise RuntimeException(f'Model with id {pk} not found')
        await session.delete(model)

    async def delete(self, session: AsyncSession, model: SQL_MODEL_TYPE) -> None:
        await session.delete(model)

    @abstractmethod
    def _filter(self, sql: Select[tuple[SQL_MODEL_TYPE]], param: FILTER_TYPE) -> Select[tuple[SQL_MODEL_TYPE]]:
        """
        筛选
        :param param:
        :return:
        """
        raise NotImplementedError

    def _common_filter(self, param: FILTER_TYPE) -> Select[tuple[SQL_MODEL_TYPE]]:
        """
        通用筛选
        :param param:
        :return:
        """
        sql = select(self._model_class())
        if param.order_bys:
            for order_by in param.order_bys:
                sql = sql.order_by(order_by)

        return self._filter(sql, param)

    def _apply_page(self, sql: Select[tuple[SQL_MODEL_TYPE]], param: FILTER_TYPE) -> Select[tuple[SQL_MODEL_TYPE]]:
        if param.limit is not None:
            sql = sql.limit(param.limit)

        if param.page is not None:
            sql = sql.offset(param.get_offset())

        return sql
