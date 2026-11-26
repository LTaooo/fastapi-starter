import asyncio
import time
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.app_config import AppConfig
from config.crontab_config import CrontabConfig
from core.config import Config
from core.logger import Logger
from core.redis.redis import Redis
from core.singleton_meta import SingletonMeta

_RENEW_LOCK_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('expire', KEYS[1], ARGV[2])
end
return 0
"""

_RELEASE_LOCK_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""


class Crontab(metaclass=SingletonMeta):
    """定时任务调度器；开启 singleton 时只有持有 Redis 锁的实例派发任务，锁按 TTL 续期。

    单例保证调度者唯一而非业务执行互斥：故障切换窗口内两个实例可能各派发一次任务，
    同一次业务执行的跨实例互斥由任务自身保证；锁丢失或本地租约过期只停止后续派发，
    已在执行的任务会继续跑完。
    """

    # 锁的 Redis 有效期，同时是本实例判定租约过期、停止派发的时限
    _LOCK_TTL_SECONDS = 60
    # 取租期的三分之一：留出重试余地，续期失败不会立刻掉锁；同时是抢锁重试与丢锁检测的周期
    _LOCK_MAINTAIN_SECONDS = _LOCK_TTL_SECONDS // 3
    # apscheduler 默认宽松期为 1 秒，事件循环阻塞超过 1 秒时本次触发会被丢弃
    _JOB_DEFAULTS = {'misfire_grace_time': 60}

    def __init__(self) -> None:
        self._scheduler: AsyncIOScheduler | None = None
        self._lock_task: asyncio.Task[None] | None = None
        self._lock_value = ''
        self._lock_held = False
        self._lock_wait_logged = False
        self._lock_deadline = 0.0

    async def start(self) -> None:
        """启动调度器；singleton 模式下未持有锁的实例保持空转，由维护任务持续尝试接管。"""
        if self._scheduler is not None:
            return
        config = Config.get(CrontabConfig)
        if not config.enable:
            return

        scheduler = AsyncIOScheduler(timezone=config.timezone, job_defaults=self._JOB_DEFAULTS)
        scheduler.start()
        self._scheduler = scheduler

        if not config.singleton or not Redis().is_enable():
            if config.singleton:
                Logger.get().warning('Redis未启用, 各实例都会执行定时任务')
            self._register_jobs(scheduler)
        else:
            # 锁值取进程内随机标识：容器中各实例的主进程 PID 相同，仅用 PID 无法区分持有者
            self._lock_value = uuid4().hex
            self._lock_task = asyncio.create_task(self._maintain_lock(scheduler))
        Logger.get().info('定时任务启动完成 singleton={} timezone={}', config.singleton, config.timezone)

    async def stop(self) -> None:
        """停止派发、释放锁并关闭调度器；单步失败不跳过其余清理，重复调用安全。"""
        await self._cancel_lock_task()

        scheduler = self._scheduler
        self._scheduler = None
        if scheduler is not None:
            try:
                # 先摘任务再关调度器：释放锁之前本实例必须确定不再派发
                scheduler.remove_all_jobs()
                scheduler.shutdown()
            except Exception as e:
                Logger.get().error('定时任务调度器关闭失败 reason={}', e)

        if self._lock_value:
            # 维护任务可能刚写完锁就被取消，因此不看 _lock_held，统一按持有者校验兜底清理
            self._lock_held = False
            await self._release_lock()

    async def _cancel_lock_task(self) -> None:
        """取消维护任务；任务自身的异常在此消化，避免中断 stop 的后续清理。"""
        lock_task = self._lock_task
        self._lock_task = None
        if lock_task is None:
            return

        lock_task.cancel()
        try:
            await lock_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            Logger.get().error('定时任务单例锁维护任务异常退出 reason={}', e)

    async def _maintain_lock(self, scheduler: AsyncIOScheduler) -> None:
        """按维护周期抢锁或续期；单个周期的异常只记录日志，保证租约判断不因任务退出而失效。"""
        while True:
            try:
                if self._lock_held:
                    await self._renew_lock(scheduler)
                else:
                    await self._try_acquire_lock(scheduler)
            except Exception as e:
                Logger.get().error('定时任务锁维护周期异常 reason={}', e)
            await asyncio.sleep(self._LOCK_MAINTAIN_SECONDS)

    async def _try_acquire_lock(self, scheduler: AsyncIOScheduler) -> None:
        """抢锁成功后注册任务；被其他实例占有时留到下个周期重试。"""
        try:
            client = Redis().get_instance()
            acquired = bool(await client.set(self._lock_key(), self._lock_value, nx=True, ex=self._LOCK_TTL_SECONDS))
        except Exception as e:
            Logger.get().error('定时任务单例锁获取失败, 下个周期重试 reason={}', e)
            return
        if not acquired:
            if not self._lock_wait_logged:
                # 只记录一次，避免实例长期空转时每个周期都写日志
                self._lock_wait_logged = True
                Logger.get().info('定时任务单例锁已被其他实例持有, 本实例等待接管')
            return

        self._lock_deadline = time.monotonic() + self._LOCK_TTL_SECONDS
        try:
            self._register_jobs(scheduler)
        except Exception as e:
            # 注册失败时不占着锁空转：撤销半注册的任务，把锁让给其他实例
            scheduler.remove_all_jobs()
            await self._release_lock()
            Logger.get().error('定时任务注册失败, 已释放单例锁 reason={}', e)
            return

        self._lock_wait_logged = False
        self._lock_held = True
        Logger.get().info('定时任务单例锁已获取 lockValue={}', self._lock_value)

    async def _renew_lock(self, scheduler: AsyncIOScheduler) -> None:
        """续期锁；锁被他人接管或续期失败超过本地租约截止时间时停止本实例派发。"""
        try:
            script = Redis().get_instance().register_script(_RENEW_LOCK_SCRIPT)
            renewed = await script(keys=[self._lock_key()], args=[self._lock_value, self._LOCK_TTL_SECONDS])
        except Exception as e:
            Logger.get().error('定时任务单例锁续期失败, 下个周期重试 reason={}', e)
            if time.monotonic() < self._lock_deadline:
                return
            self._on_lock_lost(scheduler, '续期持续失败且租约已过期')
            return

        if renewed:
            self._lock_deadline = time.monotonic() + self._LOCK_TTL_SECONDS
            return
        self._on_lock_lost(scheduler, '锁已被其他实例接管')

    def _on_lock_lost(self, scheduler: AsyncIOScheduler, reason: str) -> None:
        """停止本实例的后续派发；已在执行的任务不受影响。"""
        self._lock_held = False
        self._lock_deadline = 0.0
        scheduler.remove_all_jobs()
        Logger.get().error('定时任务单例派发已停止 reason={}', reason)

    async def _release_lock(self) -> None:
        """释放本实例持有的锁；释放失败只记录日志，锁会在 TTL 到期后失效。"""
        try:
            script = Redis().get_instance().register_script(_RELEASE_LOCK_SCRIPT)
            await script(keys=[self._lock_key()], args=[self._lock_value])
        except Exception as e:
            Logger.get().error('定时任务单例锁释放失败, 锁将超时自动失效 reason={}', e)

    def _register_jobs(self, scheduler: AsyncIOScheduler) -> None:
        """交由配置声明任务清单，并在声明完成后记录实际注册的任务。"""
        Config.get(CrontabConfig).register_jobs(scheduler)
        names = ', '.join(job.name for job in scheduler.get_jobs()) or '无'
        Logger.get().info('定时任务注册完成 jobs={}', names)

    def _lock_key(self) -> str:
        return f'{Config.get(AppConfig).app_name}_crontab_lock'
