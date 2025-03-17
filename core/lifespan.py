from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.context import Context
from core.mysql.mysql import Mysql


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _before_startup()
    yield
    await _after_startup()


async def _before_startup():
    Mysql()


async def _after_startup():
    await Mysql().close()
    Context.clear()
