from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Generic, TypeVar

from faststream.middlewares import AckPolicy
from faststream.rabbit import Channel, RabbitQueue
from pydantic import BaseModel

from core.rabbitmq.consumer import register_consumer
from core.rabbitmq.rabbitmq import RabbitMQ

Message = TypeVar('Message', bound=BaseModel)


class QueueInterface(Generic[Message], ABC):
    """约束队列声明与类型化消费，共享发布和订阅策略。"""

    @property
    @abstractmethod
    def queue(self) -> RabbitQueue:
        """返回队列描述；具体实现应在配置加载后首次使用时构造并缓存。"""
        raise NotImplementedError

    @abstractmethod
    async def consume(self, message: Message) -> None:
        """处理消息；具体实现必须显式标注消息类型，供 broker 反序列化。"""
        raise NotImplementedError

    async def publish(self, message: Message) -> None:
        """通过队列的路由键发布消息，使用统一交换机与持久化策略。"""
        await RabbitMQ().publish(message, routing_key=self.queue.routing_key)

    def is_enabled(self) -> bool:
        """决定是否注册消费订阅，不限制显式消息发布。"""
        return True

    @property
    def ack_policy(self) -> AckPolicy:
        """消费失败时拒绝消息且不重新入队。"""
        return AckPolicy.REJECT_ON_ERROR

    @property
    def channel(self) -> Channel | None:
        """未指定专用通道时使用 RabbitMQ 连接配置中的默认预取数量。"""
        return None


_registered_queue_types: set[type[QueueInterface[Any]]] = set()


def register_queues(queue_types: Iterable[type[QueueInterface[Any]]]) -> None:
    """在首次构建 broker 前装配队列类，成功注册的类在同一进程中不重复登记。"""
    for queue_type in queue_types:
        if queue_type in _registered_queue_types:
            continue
        instance = queue_type()
        if not instance.is_enabled():
            continue
        register_consumer(instance.queue, ack_policy=instance.ack_policy, channel=instance.channel)(instance.consume)
        _registered_queue_types.add(queue_type)
