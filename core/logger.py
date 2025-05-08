from loguru import logger as loguru_logger
import sys
import os
from core.singleton_meta import SingletonMeta


class Logger(metaclass=SingletonMeta):
    __logger = loguru_logger
    _log_file: str
    _is_init: bool = False

    @classmethod
    def init(cls):
        if cls._is_init:
            return

        cls._log_file = os.path.join(cls.find_project_root(), 'runtime', 'app.log')
        print(cls._log_file)
        cls._is_init = True
        os.makedirs(os.path.dirname(cls._log_file), exist_ok=True)

        cls.__logger.remove()
        level = 'INFO'

        cls.__logger.add(
            sys.stdout,
            level=level,
            colorize=True,
            format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
            enqueue=True,
        )
        cls.__logger.add(
            cls._log_file,
            level=level,
            rotation='100 MB',
            retention='10 days',
            encoding='utf-8',
            format='{{"time":"{time:YYYY-MM-DD HH:mm:ss}","level":"{level}","message":"{message}","module":"{module}","file":"{file.path}","function":"{function}","line":"{line}"}}',
            enqueue=True,
        )

    @classmethod
    def get(cls):
        cls.init()
        return cls.__logger

    @classmethod
    def add_sink(cls, *args, **kwargs):
        cls.get().add(*args, **kwargs)

    @classmethod
    def find_project_root(cls, markers=('pyproject.toml', '.git')):
        """
        查找项目根目录
        :param markers: 项目根目录的特征文件或文件夹
        :return: 项目根目录的绝对路径
        """
        path = os.path.abspath(os.path.dirname(__file__))
        while path != os.path.dirname(path):
            if any(os.path.exists(os.path.join(path, marker)) for marker in markers):
                return path
            path = os.path.dirname(path)
        return os.getcwd()
