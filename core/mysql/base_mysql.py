from abc import ABC, ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator, ClassVar, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config.mysql_config import MysqlConfig
from core.mysql.base_mysql_session import BaseMysqlSession
from core.singleton_meta import SingletonMeta

_SESSION = TypeVar('_SESSION', bound=BaseMysqlSession)


class SingletonABCMeta(ABCMeta, SingletonMeta):
    pass


class BaseMysql(ABC, Generic[_SESSION], metaclass=SingletonABCMeta):
    _engine: ClassVar[AsyncEngine]

    @classmethod
    def init(cls):
        config = cls.get_config()
        cls._engine = create_async_engine(
            f'mysql+aiomysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}',
            pool_size=5,
            max_overflow=10,
            echo=config.echo,
        )

    @classmethod
    @abstractmethod
    def get_config(cls) -> MysqlConfig:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def session_class(cls) -> Type[_SESSION]:
        raise NotImplementedError()

    @classmethod
    @asynccontextmanager
    async def _session(cls) -> AsyncGenerator[AsyncSession, None]:
        session = AsyncSession(cls._engine, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()

    @classmethod
    @asynccontextmanager
    async def with_session(cls) -> AsyncGenerator[_SESSION, None]:
        """
        获取一个异步MySQL会话, 不会自动commit和rollback, 如果涉及写操作, 需要手动commit
        """
        async with cls._session() as session:
            yield cls.session_class()(session)

    @classmethod
    async def get_session(cls) -> _SESSION:
        async with cls._session() as session:
            return cls.session_class()(session)

    @classmethod
    async def close(cls):
        await cls._engine.dispose()
