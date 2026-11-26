from contextlib import asynccontextmanager
from fastapi import FastAPI

from config.app_config import AppConfig
from config.nacos_config import NacosConfig
from config.queue_config import QueueConfig
from core.config import Config
from core.crontab.crontab import Crontab
from core.logger import Logger
from core.mysql.database.app.app_database import AppDatabase
from core.nacos.nacos import Nacos
from core.rabbitmq import RabbitMQ
from core.redis.redis import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await _before_startup()
        await _after_startup()
        yield
    finally:
        await _before_shutdown()


async def _before_startup():
    """加载配置并初始化基础设施，在 RabbitMQ 启动前显式注册消费者。"""
    nacos_config = Config.get(NacosConfig)
    await Nacos().init(nacos_config)
    Config().update_config(await Nacos().get_config(nacos_config.get_config_data()))
    Logger.init()
    AppDatabase.init()
    await Redis().connect()
    QueueConfig.register()
    await RabbitMQ().start()
    await Crontab().start()


async def _before_shutdown():
    await RabbitMQ().stop()
    await Crontab().stop()
    await AppDatabase.close()
    await Redis().disconnect()
    await Nacos().close()


async def _after_startup():
    """输出启动结果及包含部署路径前缀的本机文档访问链接。"""
    app_config = Config.get(AppConfig)
    host = '127.0.0.1' if app_config.app_host in ('0.0.0.0', '::') else app_config.app_host
    if ':' in host:
        host = f'[{host}]'
    root_path = app_config.app_root_path.rstrip('/')
    doc_url = f'http://{host}:{app_config.app_port}{root_path}{app_config.docs_path}' if app_config.is_docs_enabled() else '未启用'
    Logger.get().info('项目启动成功 doc={} app={} env={}', doc_url, app_config.app_name, app_config.app_env.value)
