from abc import ABC
from contextlib import asynccontextmanager

from sqlmodel.ext.asyncio.session import AsyncSession


class BaseMysqlSession(ABC):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._depth = 0

    def get_session(self):
        return self._session

    async def commit(self):
        return await self._session.commit()

    @asynccontextmanager
    async def transaction(self, nested=False):
        """
        Args:
            nested: 是否嵌套事务
        """
        self._depth += 1
        is_nested = self._depth > 1 or nested
        try:
            if not is_nested:
                async with self._session.begin():
                    yield
            else:
                async with self._session.begin_nested():
                    yield
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise
        finally:
            self._depth -= 1
