import os
from typing import Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.singleton_meta import SingletonMeta


class MysqlConfig(BaseModel):
    hostname: str
    database: str
    username: str
    password: str
    port: str
    echo: bool


class Mysql(metaclass=SingletonMeta):
    _engine: Optional[AsyncEngine]

    @classmethod
    def _get_config(cls) -> "MysqlConfig":
        load_dotenv()
        return MysqlConfig(
            hostname=os.getenv("MYSQL_HOST"),
            database=os.getenv("MYSQL_DB"),
            username=os.getenv("MYSQL_USER"),
            password=quote_plus(os.getenv("MYSQL_PASSWORD")),
            port=os.getenv("MYSQL_PORT"),
            echo=bool(os.getenv("MYSQL_ECHO")),
        )

    def __init__(self):
        config = self._get_config()
        self._engine = create_async_engine(
            f"mysql+aiomysql://{config.username}:{config.password}@{config.hostname}:{config.port}/{config.database}",
            pool_size=5,
            max_overflow=10,
            echo=config.echo
        )

    def session(self) -> AsyncSession:
        return AsyncSession(self._engine)
