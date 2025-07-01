from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.nacos_config import NacosConfig
from core.config import Config
from core.crontab import crontab
from core.mysql.database.book.book_database import BookDatabase
from core.nacos.nacos import Nacos
from core.rabbitmq.rabbitmq import RabbitMQ
from core.redis.redis import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _before_startup()
    yield
    await _after_startup()


async def _before_startup():
    nacos_config = Config.get(NacosConfig)
    await Nacos().init(nacos_config)
    Config().update_config(await Nacos().get_config(nacos_config.get_config_data()))
    BookDatabase.init()
    Redis().get_instance()
    await RabbitMQ().connect()
    await crontab.register()


async def _after_startup():
    await crontab.shutdown()
    await BookDatabase.close()
    await Redis().disconnect()
    await Nacos().close()
    await RabbitMQ().close()
