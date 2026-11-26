import asyncio
from functools import cached_property

from faststream.rabbit import Channel, RabbitQueue
from pydantic import BaseModel, Field

from config.app_config import AppConfig
from core.config import Config
from core.logger import Logger
from core.rabbitmq import QueueInterface


class DemoMessage(BaseModel):
    content: str = Field(description='消息内容')


class DemoQueue(QueueInterface[DemoMessage]):
    """开发环境演示队列，使用持久化队列并逐条预取消息。"""

    @cached_property
    def queue(self) -> RabbitQueue:
        """首次使用时按应用名称构造队列，发布与订阅使用相同路由键。"""
        name = f'{Config.get(AppConfig).app_name}_demo'
        return RabbitQueue(name=name, durable=True, routing_key=name)

    def is_enabled(self) -> bool:
        """仅在开发环境注册演示消费者。"""
        return Config.get(AppConfig).is_dev()

    @property
    def channel(self) -> Channel:
        """每次只预取一条消息。"""
        return Channel(prefetch_count=1)

    async def consume(self, message: DemoMessage) -> None:
        """消费演示消息；内容为 1 时抛出异常，由 ack 策略拒绝且不重新入队。"""
        if message.content == '1':
            raise RuntimeError('测试异常')
        Logger.get().info('接收到消息 content={}', message.content)
        await asyncio.sleep(5)
        Logger.get().info('消息处理完成 content={}', message.content)
