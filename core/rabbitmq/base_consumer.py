from abc import ABC, abstractmethod
from enum import Enum

from aio_pika.abc import AbstractIncomingMessage

from config.app_config import AppConfig
from core.config import Config


class Result(int, Enum):
    OK = 1
    REJECT = 2
    RETRY = 3


# noinspection PyMethodMayBeStatic
class BaseConsumer(ABC):
    @abstractmethod
    async def consume(self, message: AbstractIncomingMessage) -> Result:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_queue_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_routing_key(cls) -> str:
        return Config.get(AppConfig).app_name + '_task_routing_key'

    @classmethod
    def get_qos(cls) -> int:
        return 10
