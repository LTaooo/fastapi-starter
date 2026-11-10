import atexit
import logging
import os
import sys
from pathlib import Path

from loguru import logger

from config.app_config import AppConfig
from config.log_config import LogConfig
from core.config import Config
from core.util.helper import Helper

_LOG_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | '
    '<cyan>{process.name}:{process.id}</cyan> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
)


class InterceptHandler(logging.Handler):
    """把标准库 logging 的记录转发给 loguru，保证第三方库日志使用同一套输出。"""

    def emit(self, record: logging.LogRecord) -> None:
        """转换日志级别并转发记录，同时跳过 logging 内部帧以保留真实调用位置。"""
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 0
        while frame is not None and frame.f_globals.get('__name__') in ('logging', __name__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Logger:
    """loguru 的初始化入口。应用启动时调用一次 init，运行期通过 get 获取 logger。"""

    _is_init: bool = False

    @classmethod
    def init(cls) -> None:
        """初始化日志输出；同一进程内幂等，重复调用不会重复添加 handler。"""
        if cls._is_init:
            return

        app_config = Config.get(AppConfig)
        log_config = Config.get(LogConfig)
        log_level = log_config.level.upper()

        logger.remove()
        logger.add(
            sys.stdout,
            level=log_level,
            colorize=None,
            format=_LOG_FORMAT,
            backtrace=True,
            diagnose=False,
        )

        if log_config.file_enable:
            # 多进程同时轮转同一个文件会产生竞争，按进程拆分文件；单进程保持固定文件名。
            with_pid = app_config.workers > 1
            logger.add(
                cls._get_log_file(app_config.app_name, 'info', with_pid),
                level=log_level,
                colorize=False,
                format=_LOG_FORMAT,
                rotation=log_config.rotation,
                retention=log_config.retention,
                encoding='utf-8',
                enqueue=True,
                backtrace=True,
                diagnose=False,
                filter=lambda record: record['level'].no < logging.ERROR,
            )
            logger.add(
                cls._get_log_file(app_config.app_name, 'error', with_pid),
                level='ERROR',
                colorize=False,
                format=_LOG_FORMAT,
                rotation=log_config.rotation,
                retention=log_config.retention,
                encoding='utf-8',
                enqueue=True,
                backtrace=True,
                diagnose=False,
            )

        cls._install_logging_bridge()
        atexit.register(logger.complete)
        cls._is_init = True

    @staticmethod
    def _install_logging_bridge() -> None:
        """接管标准库 logging 与 uvicorn 的 logger，避免日志重复输出或丢失。"""
        handler = InterceptHandler()
        root_logger = logging.getLogger()
        root_logger.handlers = [handler]
        root_logger.setLevel(logging.NOTSET)

        # uvicorn 命令行启动时会为自己的 logger 安装 handler 并关闭传播，需一并接管。
        for name in ('uvicorn', 'uvicorn.error', 'uvicorn.access'):
            uvicorn_logger = logging.getLogger(name)
            uvicorn_logger.handlers = [handler]
            uvicorn_logger.propagate = False

    @staticmethod
    def _get_log_file(service_name: str, level: str, with_pid: bool) -> str:
        """创建日志目录并返回文件路径；多进程时追加 PID 以避免并发轮转同一个文件。"""
        filename = f'{service_name}-{level}'
        if with_pid:
            filename = f'{filename}-{os.getpid()}'
        log_file = Helper.with_root_path(['logs', service_name, level, f'{filename}.log'])
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        return log_file

    @classmethod
    def get(cls):
        """返回全局 logger；应用启动阶段应先调用 init 完成配置。"""
        return logger
