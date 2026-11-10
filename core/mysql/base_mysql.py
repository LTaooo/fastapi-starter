from abc import ABC, ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator, ClassVar, Type, TypeVar, Generic
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession

from config.mysql_config import MysqlConfig
from core.singleton_meta import SingletonMeta

_SESSION = TypeVar('_SESSION', bound=AsyncSession)


class SingletonABCMeta(ABCMeta, SingletonMeta):
    pass


class BaseMysql(ABC, Generic[_SESSION], metaclass=SingletonABCMeta):
    _engine: ClassVar[AsyncEngine | None] = None

    @classmethod
    def init(cls):
        config = cls.get_config()
        if not config.enable:
            return
        url = URL.create(
            drivername='mysql+aiomysql',
            username=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )
        cls._engine = create_async_engine(
            url,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
            pool_pre_ping=config.pool_pre_ping,
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
    async def _session(cls) -> AsyncGenerator[_SESSION, None]:
        if cls._engine is None:
            raise RuntimeError('MySQL未启用或未初始化')
        session = cls.session_class()(cls._engine, expire_on_commit=False)
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise
        finally:
            await session.close()

    @classmethod
    @asynccontextmanager
    async def with_session(cls) -> AsyncGenerator[_SESSION, None]:
        async with cls._session() as session:
            yield session

    @classmethod
    async def get_session(cls) -> AsyncGenerator[_SESSION, None]:
        async with cls._session() as session:
            yield session

    @classmethod
    async def close(cls):
        if cls._engine is None:
            return
        await cls._engine.dispose()
        cls._engine = None
