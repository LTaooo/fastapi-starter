from abc import ABC
from contextlib import asynccontextmanager

from sqlmodel.ext.asyncio.session import AsyncSession


class BaseMysqlSession(ABC):
    def __init__(self, session: AsyncSession):
        self._session = session

    def get_session(self):
        return self._session

    async def commit(self):
        return await self._session.commit()

    @asynccontextmanager
    async def transaction(self):
        try:
            async with self._session.begin():
                yield
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            raise e
