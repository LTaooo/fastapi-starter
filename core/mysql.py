import os
from abc import abstractmethod, ABC, ABCMeta
from typing import Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

load_dotenv()


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonABCMeta(ABCMeta, SingletonMeta):
    pass


class MysqlConfig(BaseModel):
    hostname: str
    database: str
    username: str
    password: str
    port: str
    echo: bool


class Mysql(metaclass=SingletonABCMeta):
    _engine: Optional[AsyncEngine]
    # session: sessionmaker[AsyncSession]

    def _get_config(self) -> "MysqlConfig":
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
        # self.session = sessionmaker(
        #     self._engine, expire_on_commit=False, class_=AsyncSession
        # )

    def session(self):
        return AsyncSession(self._engine)
