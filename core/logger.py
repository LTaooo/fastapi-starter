import logging

from loguru import logger as loguru_logger
import sys
import os

from config.app_config import AppConfig
from core.config import Config
from core.singleton_meta import SingletonMeta
from core.util.helper import Helper


class Logger(metaclass=SingletonMeta):
    __logger = loguru_logger
    _log_file: str
    _is_init: bool = False
    service_name: str = Config.get(AppConfig).app_name

    @classmethod
    def init(cls):
        if cls._is_init:
            return
        cls.__logger.remove()
        cls._is_init = True

        cls.__logger.add(
            sys.stdout,
            level='INFO',
            colorize=True,
            format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
            enqueue=True,
        )

        format_str = (
            '{{"timestamp":"{time:YYYY-MM-DDTHH:mm:ss.SSSZ}","level":"{level}","service":"'
            f'{cls.service_name}'
            '","thread":"{thread}","message":"{message}","logger":"{module}","file":"{file.path}","function":"{function}","line":"{line}"}}'
        )
        cls.__logger.add(
            cls._get_log_file('INFO'),
            level='INFO',
            rotation='50 MB',
            retention='10 days',
            encoding='utf-8',
            filter=lambda record: logging.INFO <= record['level'].no <= logging.WARNING,
            format=format_str,
            enqueue=True,
        )
        cls.__logger.add(
            cls._get_log_file('ERROR'),
            level='ERROR',
            rotation='50 MB',
            retention='10 days',
            encoding='utf-8',
            filter=lambda record: record['level'].no >= logging.ERROR,
            format=format_str,
            enqueue=True,
        )

    @classmethod
    def _get_log_file(cls, level: str):
        level = level.lower()
        paths = ['logs', cls.service_name, level, f'{cls.service_name}-{level}.log']
        log_file = str(Helper.with_root_path(paths))
        os.makedirs(os.path.dirname(log_file), exist_ok=True, mode=0o644)
        return log_file

    @classmethod
    def get(cls):
        cls.init()
        return cls.__logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = Logger.get().level(record.levelname).name
        except (ValueError, AttributeError):
            level = record.levelno

        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_globals.get('__name__') == 'logging':
            frame = frame.f_back
            depth += 1

        Logger.get().opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)


def init():
    Logger.init()
