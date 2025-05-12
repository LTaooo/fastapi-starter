from contextlib import asynccontextmanager
from fastapi import FastAPI

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
    Nacos()


async def _after_startup():
    await BookDatabase().close()
    await Redis().disconnect()
    Nacos().unregister_service()
