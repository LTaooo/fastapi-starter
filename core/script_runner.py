"""通用脚本执行入口：在应用完整生命周期内运行异步脚本动作。

脚本动作在 lifespan 启动数据库、Redis、消息队列等组件之后执行，结束后按统一规则释放资源；
用户中断返回退出码 130，未预期异常记录日志并返回 1。
"""

import asyncio
from collections.abc import Awaitable, Callable

from core.lifespan import lifespan
from core.logger import Logger
from main import app

ScriptAction = Callable[[], Awaitable[int]]


async def run_in_lifespan(action: ScriptAction) -> int:
    """在完整应用生命周期内执行脚本动作，返回其退出码。"""
    async with lifespan(app):
        return await action()


def run_script(action: ScriptAction, script_name: str) -> int:
    """执行脚本动作，统一处理用户中断和未预期异常。"""
    try:
        return asyncio.run(run_in_lifespan(action))
    except KeyboardInterrupt:
        Logger.get().warning('脚本被用户中断 scriptName={}', script_name)
        return 130
    except Exception as exc:
        Logger.get().error('脚本异常结束 scriptName={} reason={}', script_name, f'{type(exc).__name__}: {exc}')
        return 1
