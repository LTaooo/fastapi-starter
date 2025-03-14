from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.context import Context
from core.mysql.mysql import Mysql


@asynccontextmanager
async def lifespan(app: FastAPI):
    mysql = Mysql()
    yield
    Context.clear()
    await mysql.close()