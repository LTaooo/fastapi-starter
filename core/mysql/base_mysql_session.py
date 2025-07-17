from abc import ABC
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class BaseMysqlSession(ABC):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._depth = 0

    def get_session(self) -> AsyncSession:
        return self._session

    async def commit(self):
        return await self._session.commit()

    @asynccontextmanager
    async def transaction(self):
        self._depth += 1
        is_nested = self._depth > 1 or self._session.in_transaction()
        try:
            if not is_nested:
                async with self._session.begin():
                    yield
            else:
                async with self._session.begin_nested():
                    yield
        finally:
            self._depth -= 1
