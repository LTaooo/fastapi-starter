import asyncio
import logging
from typing import Type

from core.config import Config
from core.logger import Logger
from core.rabbitmq.base_consumer import Result, BaseConsumer
from core.singleton_meta import SingletonMeta
import aio_pika
from aio_pika import logger
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool


class RabbitMQ(metaclass=SingletonMeta):
    connection_pool: Pool

    def __init__(self):
        from config.rabbitmq_config import RabbitMQConfig

        self.config: RabbitMQConfig = Config.get(RabbitMQConfig)

    async def _get_connection(self) -> AbstractRobustConnection:
        return await aio_pika.connect_robust(
            host=self.config.host,
            port=self.config.port,
            login=self.config.username,
            password=self.config.password,
            virtualhost=self.config.vhost,
            timeout=3,
        )

    def is_enable(self) -> bool:
        return self.config.enable

    async def connect(self):
        if not self.config.enable:
            return
        logger.setLevel(logging.ERROR)
        self.connection_pool: Pool = Pool(self._get_connection, max_size=self.config.connection_pool)
        channel = await self.get_channel()
        await channel.declare_exchange(self.config.exchange, aio_pika.ExchangeType.DIRECT)
        for consumer_class in self.config.get_consumers():
            asyncio.create_task(self.consume(consumer_class))

    async def get_channel(self) -> aio_pika.Channel:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def consume(self, consumer_class: Type[BaseConsumer]) -> None:
        channel = await self.get_channel()

        await channel.set_qos(consumer_class.get_qos())
        queue = await channel.declare_queue(
            consumer_class.get_queue_name(),
            durable=True,  # 队列持久化
            auto_delete=False,
        )
        # 绑定队列到交换机
        exchange = await channel.get_exchange(self.config.exchange)
        await queue.bind(exchange, consumer_class.get_routing_key())
        Logger.get().info(f'消费队列: {consumer_class.get_queue_name()} 监听成功')

        async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
            consumer_instance = consumer_class(message)
            try:
                result = await consumer_instance.consume()
                if result == Result.OK:
                    await message.ack()
                elif result == Result.REJECT:
                    await message.reject(requeue=False)
                elif result == Result.REQUEUE:
                    await message.reject(requeue=True)
            except Exception as e:
                Logger.get().error(f'消费队列: {consumer_class.get_queue_name()} 消费失败: {e}')
                await message.reject(requeue=False)

        await queue.consume(process_message, no_ack=False)

    async def publish(self, message: str, routing_key: str) -> None:
        channel = await self.get_channel()
        exchange = await channel.get_exchange(self.config.exchange)
        await exchange.publish(aio_pika.Message(body=message.encode()), routing_key=routing_key)

    async def close(self):
        if not self.config.enable:
            return
        await self.connection_pool.close()
