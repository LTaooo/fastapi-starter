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
    """返回消费者登记函数，仅记录订阅信息，不建立连接。

    所有消费者必须在首次构建 broker 前显式完成注册，构建后新增的注册不会自动绑定。
    """

    def decorator(handler: ConsumerHandler) -> ConsumerHandler:
        _consumers.append(ConsumerSpec(queue=queue, handler=handler, ack_policy=ack_policy, channel=channel))
        return handler

    return decorator


def get_consumers() -> tuple[ConsumerSpec, ...]:
    """返回已登记的消费者快照。"""
    return tuple(_consumers)
