import asyncio

from aio_pika.abc import AbstractIncomingMessage

from config.app_config import AppConfig
from core.config import Config
from core.logger import Logger
from core.rabbitmq.base_consumer import BaseConsumer, Result
from core.rabbitmq.base_producer import BaseProducer
from core.rabbitmq.rabbitmq import RabbitMQ


class DemoConsumer(BaseConsumer):
    async def consume(self, message: AbstractIncomingMessage) -> Result:
        data = message.body.decode()
        return await self.on_message(data)

    @classmethod
    async def on_message(cls, message: str) -> Result:
        await asyncio.sleep(2)
        Logger.get().info(f'处理消息: {message}')
        return Result.OK

    @classmethod
    def get_queue_name(cls) -> str:
        return Config.get(AppConfig).app_name + '_demo_queue'

    @classmethod
    def get_qos(cls) -> int:
        return 3


class DemoProducer(BaseProducer):
    @classmethod
    async def create(cls, message: str, to_queue: bool):
        mq = RabbitMQ()
        if not to_queue or not mq.is_enable():
            await DemoConsumer.on_message(message)
        else:
            await RabbitMQ().publish(message, cls.get_routing_key())
