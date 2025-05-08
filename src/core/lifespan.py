from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.context import Context
from core.mysql.database.book.book_database import BookDatabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _before_startup()
    yield
    await _after_startup()


async def _before_startup():
    BookDatabase()


async def _after_startup():
    await BookDatabase().close()
    Context.clear()
