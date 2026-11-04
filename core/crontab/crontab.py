from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.crontab_config import CrontabConfig
from config.redis_config import RedisConfig
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
        if not Config.get(RedisConfig).enable:
            Logger.get().warning('Redis未启用, 跳过定时任务单例锁')
        else:
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
    if Config.get(RedisConfig).enable:
        await Redis().get_instance().delete(config.get_singleton_key())
    _scheduler.shutdown()
