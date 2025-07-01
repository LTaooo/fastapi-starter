from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.crontab_config import CrontabConfig
from core.config import Config
from core.logger import Logger
from core.redis.redis import Redis

_scheduler = AsyncIOScheduler()


async def register():
    config = Config().get(CrontabConfig)
    if not config.enable:
        return

    _scheduler.start()

    if config.singleton:
        redis = Redis().get_instance()
        if not await redis.setnx(config.get_singleton_key(), 1):
            Logger.get().info('定时任务已存在, 跳过注册')
            return
    await config.register_jobs(_scheduler)
    Logger.get().info('定时任务启动完成')


async def shutdown():
    config = Config().get(CrontabConfig)
    if not config.enable:
        return
    redis = Redis().get_instance()
    await redis.delete(config.get_singleton_key())
    _scheduler.shutdown()
