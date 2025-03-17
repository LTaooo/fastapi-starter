from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config.mysql_config import MysqlConfig
from core.config import Config
from core.singleton_meta import SingletonMeta



class Mysql(metaclass=SingletonMeta):
    _engine: AsyncEngine

    def __init__(self):
        config = Config.get(MysqlConfig)
        self._engine = create_async_engine(
            f"mysql+aiomysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}",
            pool_size=5,
            max_overflow=10,
            echo=config.echo
        )

    def session(self) -> AsyncSession:
        return AsyncSession(self._engine)
    
    async def close(self):
        await self._engine.dispose()
