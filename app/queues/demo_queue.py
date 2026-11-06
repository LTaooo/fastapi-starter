import asyncio

from faststream.middlewares import AckPolicy
from faststream.rabbit import Channel, RabbitQueue
from pydantic import BaseModel, Field

from config.app_config import AppConfig
from core.config import Config
from core.logger import Logger
from core.rabbitmq import RabbitMQ, register_consumer


class DemoMessage(BaseModel):
    content: str = Field(description='消息内容')


_DEMO_QUEUE_NAME = f'{Config.get(AppConfig).app_name}_demo'
DEMO_QUEUE = RabbitQueue(name=_DEMO_QUEUE_NAME, durable=True, routing_key=_DEMO_QUEUE_NAME)


@register_consumer(DEMO_QUEUE, ack_policy=AckPolicy.REJECT_ON_ERROR, channel=Channel(prefetch_count=1))
async def consume_demo(message: DemoMessage) -> None:
    """消费演示消息；内容为 1 时抛出异常，由 ack 策略拒绝且不重新入队。"""
    if message.content == '1':
        raise RuntimeError('测试异常')
    Logger.get().info(f'接收到消息: {message.content}')
    await asyncio.sleep(5)
    Logger.get().info(f'完成消息: {message.content}')


async def publish_demo(content: str) -> None:
    """发布一条演示消息。"""
    await RabbitMQ().publish(DemoMessage(content=content), routing_key=DEMO_QUEUE.routing_key)
