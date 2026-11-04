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
        """
        最外层事务负责提交, 包括进入前已自动开启的事务; 嵌套事务使用保存点
        """
        is_outer = self._depth == 0
        self._depth += 1
        try:
            if not is_outer:
                async with self._session.begin_nested():
                    yield
                return

            if self._session.in_transaction():
                try:
                    yield
                except BaseException:
                    await self._session.rollback()
                    raise
                await self._session.commit()
                return

            async with self._session.begin():
                yield
        finally:
            self._depth -= 1
