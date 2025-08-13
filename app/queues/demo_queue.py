import asyncio

from config.app_config import AppConfig
from core.config import Config
from core.logger import Logger
from core.rabbitmq.base_consumer import BaseConsumer, Result
from core.rabbitmq.base_producer import BaseProducer
from core.rabbitmq.rabbitmq import RabbitMQ


def _get_routing_key() -> str:
    return Config.get(AppConfig).app_name + '_demo'


class DemoConsumer(BaseConsumer):
    async def consume(self) -> Result:
        data = self.message.body.decode()
        if data == '1':
            raise Exception('测试异常')
        Logger.get().info(f'接收到消息: {data}')
        await asyncio.sleep(5)
        Logger.get().info(f'完成消息: {data}')
        return Result.OK

    @classmethod
    def get_queue_name(cls) -> str:
        return Config.get(AppConfig).app_name + '_demo'

    @classmethod
    def get_routing_key(cls) -> str:
        return _get_routing_key()

    @classmethod
    def get_qos(cls) -> int:
        return 1


class DemoProducer(BaseProducer):
    @classmethod
    async def create(cls, data: str):
        await RabbitMQ().publish(data, _get_routing_key())

    @classmethod
    def get_routing_key(cls) -> str:
        return _get_routing_key()
