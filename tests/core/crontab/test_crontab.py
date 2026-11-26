import asyncio
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.app_config import AppConfig, AppEnvEnum
from config.crontab_config import CrontabConfig
from core.config import Config
from core.crontab import crontab as crontab_module
from core.crontab.crontab import Crontab
from core.singleton_meta import SingletonMeta

# 维护周期与任务间隔缩短到毫秒级，测试仍在真实事件循环里推进状态机。
_MAINTAIN_SECONDS = 0.02
_JOB_INTERVAL_SECONDS = 0.05
_WAIT_TIMEOUT_SECONDS = 2.0
# 手动推进假时钟用的步长，必然越过锁的有效期。
_LEASE_EXPIRY_SECONDS = 3600.0


class FakeClock:
    """可手动推进的单调时钟，替换 crontab 模块内的 time.monotonic。"""

    def __init__(self) -> None:
        self._now = 0.0

    def monotonic(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


class FakeLockRedis:
    """内存版单键 Redis，覆盖 crontab 用到的 SET NX EX 与两个锁脚本的持有者校验语义。"""

    def __init__(self) -> None:
        self.value: str | None = None
        self.expire_at = 0.0
        self.fail_renew = False
        self.release_delay = 0.0
        self.renew_calls = 0

    def is_enable(self) -> bool:
        return True

    def get_instance(self) -> 'FakeLockRedis':
        return self

    def hold(self, value: str = 'other-instance') -> None:
        """模拟另一个实例持有锁。"""
        self.value = value
        self.expire_at = time.monotonic() + 60

    def release(self) -> None:
        """模拟另一个实例释放锁。"""
        self.value = None

    async def set(self, key: str, value: str, nx: bool = False, ex: int | None = None) -> bool | None:
        """按 SET NX EX 语义写入，键未过期时返回 None。"""
        self._drop_if_expired()
        if nx and self.value is not None:
            return None
        self.value = value
        self.expire_at = time.monotonic() + (ex or 0)
        return True

    def register_script(self, script: str) -> Callable[..., Awaitable[int]]:
        """按脚本内容选择内存实现；出现未知脚本说明被测代码换了脚本而替身未同步。"""
        if script == crontab_module._RENEW_LOCK_SCRIPT:
            return self._renew
        if script == crontab_module._RELEASE_LOCK_SCRIPT:
            return self._release
        raise AssertionError('未知的锁脚本')

    async def _renew(self, keys: list[str], args: list[Any]) -> int:
        self.renew_calls += 1
        if self.fail_renew:
            raise ConnectionError('Redis不可用')
        self._drop_if_expired()
        if self.value != args[0]:
            return 0
        self.expire_at = time.monotonic() + args[1]
        return 1

    async def _release(self, keys: list[str], args: list[Any]) -> int:
        await asyncio.sleep(self.release_delay)
        self._drop_if_expired()
        if self.value != args[0]:
            return 0
        self.value = None
        return 1

    def _drop_if_expired(self) -> None:
        if self.value is not None and self.expire_at <= time.monotonic():
            self.value = None


@dataclass
class CrontabEnvironment:
    """被测实例及可观测的外部状态；job 可在 start 之前替换。"""

    crontab: Crontab
    redis: FakeLockRedis
    clock: FakeClock
    executions: list[str]
    job: Callable[[], Awaitable[None]]
    register_error: Exception | None = None


@pytest.fixture
async def crontab_environment(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[CrontabEnvironment, None]:
    """隔离配置缓存、单例实例与 Redis，用内存锁和假时钟驱动 crontab 状态机。"""
    app_config = AppConfig.model_construct(app_env=AppEnvEnum.DEV, app_name='crontab-test')
    crontab_config = CrontabConfig.model_construct(enable=True, singleton=True, timezone='Asia/Shanghai')
    monkeypatch.setattr(Config, '_configs', {AppConfig: app_config, CrontabConfig: crontab_config})
    monkeypatch.setattr(SingletonMeta, '_instances', {})

    executions: list[str] = []

    async def record_execution() -> None:
        executions.append('run')

    redis = FakeLockRedis()
    environment = CrontabEnvironment(crontab=Crontab(), redis=redis, clock=FakeClock(), executions=executions, job=record_execution)

    original_register_jobs = CrontabConfig.register_jobs

    def register_jobs(scheduler: AsyncIOScheduler) -> None:
        if environment.register_error is not None:
            raise environment.register_error
        scheduler.add_job(environment.job, 'interval', seconds=_JOB_INTERVAL_SECONDS, name='测试任务')
        original_register_jobs(scheduler)

    monkeypatch.setattr(CrontabConfig, 'register_jobs', staticmethod(register_jobs))
    monkeypatch.setattr(Crontab, '_LOCK_MAINTAIN_SECONDS', _MAINTAIN_SECONDS)
    monkeypatch.setattr(crontab_module, 'Redis', lambda: redis)
    monkeypatch.setattr(crontab_module, 'time', SimpleNamespace(monotonic=environment.clock.monotonic))

    yield environment

    await environment.crontab.stop()


async def _wait_for(condition: Callable[[], bool]) -> None:
    """等待条件成立，超时即失败，避免用固定睡眠掩盖竞态。"""
    deadline = time.monotonic() + _WAIT_TIMEOUT_SECONDS
    while not condition():
        assert time.monotonic() < deadline, '等待条件超时'
        await asyncio.sleep(0.005)


def _logged_messages(logger: MagicMock, level: str, message: str) -> list[Any]:
    """筛出指定级别的日志调用，按消息模板比对。"""
    return [call for call in getattr(logger, level).call_args_list if call.args[0] == message]


async def test_waits_while_another_instance_holds_lock(crontab_environment: CrontabEnvironment) -> None:
    """锁被其他实例持有时不注册任务、不覆盖他人的锁值，等待日志只记录一次。"""
    environment = crontab_environment
    environment.redis.hold()
    logger = MagicMock()

    with patch('core.crontab.crontab.Logger.get', return_value=logger):
        await environment.crontab.start()
        await asyncio.sleep(_MAINTAIN_SECONDS * 4)
        await environment.crontab.stop()

    assert environment.executions == []
    assert environment.redis.value == 'other-instance'
    assert len(_logged_messages(logger, 'info', '定时任务单例锁已被其他实例持有, 本实例等待接管')) == 1


async def test_registration_log_lists_registered_jobs(crontab_environment: CrontabEnvironment) -> None:
    """注册日志列出实际注册的任务名，而不是记录清单之前的状态。"""
    environment = crontab_environment
    logger = MagicMock()

    with patch('core.crontab.crontab.Logger.get', return_value=logger):
        await environment.crontab.start()
        await _wait_for(lambda: len(_logged_messages(logger, 'info', '定时任务注册完成 jobs={}')) > 0)
        await environment.crontab.stop()

    [record] = _logged_messages(logger, 'info', '定时任务注册完成 jobs={}')
    assert record.args == ('定时任务注册完成 jobs={}', '测试任务')


async def test_takes_over_after_lock_released(crontab_environment: CrontabEnvironment) -> None:
    """持锁实例释放锁后，空转实例在维护周期内接管并开始派发任务。"""
    environment = crontab_environment
    environment.redis.hold()

    await environment.crontab.start()
    await asyncio.sleep(_MAINTAIN_SECONDS * 4)
    assert environment.executions == []

    environment.redis.release()
    await _wait_for(lambda: len(environment.executions) > 0)

    assert environment.redis.value not in (None, 'other-instance')


async def test_keeps_dispatching_within_lease_when_renew_fails(crontab_environment: CrontabEnvironment) -> None:
    """续期异常但本地租约未到期时继续派发，不因瞬时故障停摆。"""
    environment = crontab_environment

    await environment.crontab.start()
    await _wait_for(lambda: len(environment.executions) > 0)

    environment.redis.fail_renew = True
    executed = len(environment.executions)
    await asyncio.sleep(_MAINTAIN_SECONDS * 4)

    assert len(environment.executions) > executed
    assert environment.redis.value is not None


async def test_stops_dispatching_after_lease_expires(crontab_environment: CrontabEnvironment) -> None:
    """续期持续失败且本地租约过期后停止派发，同时保留其他实例写入的锁值。"""
    environment = crontab_environment

    await environment.crontab.start()
    await _wait_for(lambda: len(environment.executions) > 0)

    attempts = environment.redis.renew_calls
    environment.clock.advance(_LEASE_EXPIRY_SECONDS)
    environment.redis.hold('other-instance')
    environment.redis.fail_renew = True
    await _wait_for(lambda: environment.redis.renew_calls > attempts)
    await asyncio.sleep(_MAINTAIN_SECONDS * 4)

    executed = len(environment.executions)
    await asyncio.sleep(_MAINTAIN_SECONDS * 4)

    assert len(environment.executions) == executed
    assert environment.redis.value == 'other-instance'


async def test_registration_failure_releases_lock_and_cleanup_completes(crontab_environment: CrontabEnvironment) -> None:
    """注册任务抛错时交出锁并保持不派发，stop 仍能完成清理并停止维护任务。"""
    environment = crontab_environment
    environment.register_error = RuntimeError('注册任务失败')
    logger = MagicMock()

    with patch('core.crontab.crontab.Logger.get', return_value=logger):
        await environment.crontab.start()
        await asyncio.sleep(_MAINTAIN_SECONDS * 4)
        await environment.crontab.stop()

    assert environment.executions == []
    assert environment.redis.value is None
    assert len(_logged_messages(logger, 'error', '定时任务注册失败, 已释放单例锁 reason={}')) > 0

    renew_calls = environment.redis.renew_calls
    await asyncio.sleep(_MAINTAIN_SECONDS * 4)
    assert environment.redis.renew_calls == renew_calls


async def test_stop_stops_dispatching_and_releases_lock(crontab_environment: CrontabEnvironment) -> None:
    """stop 先停派发再交还锁：释放锁耗时不产生新的任务执行，返回后锁已释放。"""
    environment = crontab_environment

    await environment.crontab.start()
    await _wait_for(lambda: len(environment.executions) > 0)

    # 释放锁变慢，暴露“先释放锁、后停派发”时在锁外继续执行任务的窗口
    environment.redis.release_delay = _JOB_INTERVAL_SECONDS * 2
    await environment.crontab.stop()

    executed = len(environment.executions)
    await asyncio.sleep(_MAINTAIN_SECONDS * 4)

    assert len(environment.executions) == executed
    assert environment.redis.value is None


async def test_lock_loss_does_not_interrupt_running_job(crontab_environment: CrontabEnvironment) -> None:
    """丢锁只停止后续派发：已在执行的任务跑完，之后不再有新执行。"""
    environment = crontab_environment

    async def slow_job() -> None:
        environment.executions.append('开始')
        await asyncio.sleep(_JOB_INTERVAL_SECONDS * 4)
        environment.executions.append('结束')

    environment.job = slow_job

    await environment.crontab.start()
    await _wait_for(lambda: environment.executions == ['开始'])

    environment.redis.hold('other-instance')
    await _wait_for(lambda: '结束' in environment.executions)

    assert environment.executions == ['开始', '结束']
    await asyncio.sleep(_MAINTAIN_SECONDS * 4)
    assert environment.executions == ['开始', '结束']
