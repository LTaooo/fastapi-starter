from abc import ABC, ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config.mysql_config import MysqlConfig
from core.config import Config
from core.mysql.base_mysql_session import BaseMysqlSession
from core.singleton_meta import SingletonMeta


class SingletonABCMeta(ABCMeta, SingletonMeta):
    pass


class BaseMysql(ABC, metaclass=SingletonABCMeta):
    _engine: AsyncEngine

    def __init__(self):
        config = Config.get(MysqlConfig)
        self._engine = create_async_engine(
            f'mysql+aiomysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}',
            pool_size=5,
            max_overflow=10,
            echo=config.echo,
        )

    @abstractmethod
    def get_config(self) -> Config:
        raise NotImplementedError()

    @asynccontextmanager
    async def _session(self) -> AsyncGenerator[AsyncSession, None]:
        session = AsyncSession(self._engine)
        try:
            yield session
        finally:
            await session.close()

    @asynccontextmanager
    async def _auto_commit_session(self) -> AsyncGenerator[AsyncSession, None]:
        session = AsyncSession(self._engine)
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    @abstractmethod
    async def session(self) -> AsyncGenerator[BaseMysqlSession, None]:
        """
        获取一个异步MySQL会话, 不会自动commit和rollback, 如果涉及写操作, 需要手动commit
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    async def auto_commit_session(self) -> AsyncGenerator[BaseMysqlSession, None]:
        """
        获取一个异步MySQL会话, 会自动commit和rollback
        :return:
        """
        raise NotImplementedError()

    async def close(self):
        await self._engine.dispose()
