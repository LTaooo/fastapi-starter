from typing import Any, ClassVar

from app.queues.demo_queue import DemoQueue
from core.rabbitmq import QueueInterface, register_queues


class QueueConfig:
    """声明应用使用的队列类，由统一接口装配订阅。"""

    queues: ClassVar[tuple[type[QueueInterface[Any]], ...]] = (DemoQueue,)

    @classmethod
    def register(cls) -> None:
        """在首次构建 broker 前注册配置的队列类。"""
        register_queues(cls.queues)
