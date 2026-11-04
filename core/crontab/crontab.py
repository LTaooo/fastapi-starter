from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.crontab_config import CrontabConfig
from config.redis_config import RedisConfig
from core.config import Config
from core.logger import Logger
from core.redis.redis import Redis

_scheduler = AsyncIOScheduler()
_started = False
_lock_acquired = False
_lock_key: str | None = None


async def register():
    global _started, _lock_acquired, _lock_key
    config = Config().get(CrontabConfig)
    if not config.enable:
        return

    _scheduler.start()
    _started = True

    if config.singleton:
        if not Config.get(RedisConfig).enable:
            Logger.get().warning('Redis未启用, 跳过定时任务单例锁')
        else:
            redis = Redis().get_instance()
            _lock_key = config.get_singleton_key()
            if not await redis.setnx(_lock_key, 1):
                Logger.get().info('定时任务已存在, 跳过注册')
                return
            _lock_acquired = True
    await config.register_jobs(_scheduler)
    Logger.get().info('定时任务启动完成')


async def shutdown():
    global _started, _lock_acquired, _lock_key
    if _started:
        _scheduler.shutdown()
        _started = False
    if _lock_acquired and _lock_key is not None:
        await Redis().get_instance().delete(_lock_key)
        _lock_acquired = False
        _lock_key = None
