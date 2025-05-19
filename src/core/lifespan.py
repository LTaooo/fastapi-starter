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
    nacos_config = Config.get(NacosConfig)
    # 从Nacos加载完整配置并更新全局配置对象
    # 这会使所有从Nacos中获取的配置覆盖本地默认配置
    await Nacos().init(nacos_config)
    Config().update_config(await Nacos().get_config(nacos_config.get_config_data()))
    BookDatabase.init()
    Redis().get_instance()


async def _after_startup():
    await BookDatabase.close()
    await Redis().disconnect()
    await Nacos().close()
