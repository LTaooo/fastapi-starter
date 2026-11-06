from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypeAlias

from faststream.middlewares import AckPolicy
from faststream.rabbit import Channel, RabbitQueue

ConsumerHandler: TypeAlias = Callable[..., Awaitable[Any]]


@dataclass(slots=True)
class ConsumerSpec:
    """消费者注册信息，broker 启动时统一绑定。"""

    queue: RabbitQueue
    handler: ConsumerHandler
    ack_policy: AckPolicy = AckPolicy.REJECT_ON_ERROR
    channel: Channel | None = None


_consumers: list[ConsumerSpec] = []


def register_consumer(
    queue: RabbitQueue,
    *,
    ack_policy: AckPolicy = AckPolicy.REJECT_ON_ERROR,
    channel: Channel | None = None,
) -> Callable[[ConsumerHandler], ConsumerHandler]:
    """登记消费者；模块导入时调用，避免在导入阶段建立连接。

    所有消费者必须在 RabbitMQ.start() 之前完成注册，broker 启动后新增的注册不会生效。
    """

    def decorator(handler: ConsumerHandler) -> ConsumerHandler:
        _consumers.append(ConsumerSpec(queue=queue, handler=handler, ack_policy=ack_policy, channel=channel))
        return handler

    return decorator


def get_consumers() -> tuple[ConsumerSpec, ...]:
    """返回已登记的消费者快照。"""
    return tuple(_consumers)
