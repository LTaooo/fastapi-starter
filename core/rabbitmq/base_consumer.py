from abc import ABC, abstractmethod
from enum import Enum

from aio_pika.abc import AbstractIncomingMessage


class Result(int, Enum):
    OK = 1  # 成功
    REJECT = 2  # 拒绝
    REQUEUE = 3  # 重新入队


# noinspection PyMethodMayBeStatic
class BaseConsumer(ABC):
    message: AbstractIncomingMessage

    def __init__(self, message: AbstractIncomingMessage) -> None:
        self.message = message

    @abstractmethod
    async def consume(self) -> Result:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_queue_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_routing_key(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_qos(cls) -> int:
        return 10

    @classmethod
    def get_retry_count(cls) -> int:
        return 3
