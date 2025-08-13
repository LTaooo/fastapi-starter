from contextlib import asynccontextmanager
from fastapi import FastAPI

from config.app_config import AppConfig
from config.mcp_config import MCPConfig
from config.nacos_config import NacosConfig
from core.config import Config
from core.crontab import crontab
from core.logger import Logger
from core.mcp_server import mcp
from core.mysql.database.app.app_database import AppDatabase
from core.nacos.nacos import Nacos
from core.rabbitmq.rabbitmq import RabbitMQ
from core.redis.redis import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await _before_startup()
        if Config.get(MCPConfig).enable:
            mcp.register(app)
            async with mcp.mcp.session_manager.run():
                await _after_startup()
                yield
        else:
            await _after_startup()
            yield
    finally:
        await _before_shutdown()


async def _before_startup():
    nacos_config = Config.get(NacosConfig)
    await Nacos().init(nacos_config)
    Config().update_config(await Nacos().get_config(nacos_config.get_config_data()))
    AppDatabase.init()
    await Redis().connect()
    await RabbitMQ().connect()
    await crontab.register()


async def _before_shutdown():
    await crontab.shutdown()
    await AppDatabase.close()
    await Redis().disconnect()
    await Nacos().close()
    await RabbitMQ().close()


async def _after_startup():
    app_config = Config.get(AppConfig)
    Logger.get().info(f'项目[{app_config.app_name} - {app_config.app_env.value}]启动成功 listen:{app_config.get_bind_host()}')
