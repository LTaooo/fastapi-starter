from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.nacos_config import NacosConfig
from core.config import Config
from core.mysql.database.book.book_database import BookDatabase
from core.nacos.nacos import Nacos
from core.redis.redis import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _before_startup()
    yield
    await _after_startup()


async def _before_startup():
    BookDatabase()
    Redis().get_instance()
    await Nacos().init(Config.get(NacosConfig))


async def _after_startup():
    await BookDatabase().close()
    await Redis().disconnect()
    await Nacos().close()
