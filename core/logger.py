from loguru import logger
import sys
import os
from core.singleton_meta import SingletonMeta


class Logger(metaclass=SingletonMeta):
    __logger = logger
    log_file: str

    def __init__(self):
        self.init()

    def init(self):
        self.log_file = os.path.join('runtime', 'app.log')
        self.__logger.remove()
        self.__logger.add(
            sys.stdout,
            level='INFO',
            colorize=True,
            format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
            enqueue=True,
        )
        self.__logger.add(
            self.log_file,
            level='INFO',
            rotation='100 MB',
            retention='10 days',
            encoding='utf-8',
            format='{{"time":"{time:YYYY-MM-DD HH:mm:ss}","level":"{level}","message":"{message}","module":"{module}","file":"{file.path}","function":"{function}","line":"{line}"}}',
            enqueue=True,
        )

    @classmethod
    def get(cls):
        return cls.__logger
