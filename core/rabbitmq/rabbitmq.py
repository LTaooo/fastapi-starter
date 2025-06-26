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
        Logger.get().info('RabbitMQ: 链接成功')
        for consumer_class in self.config.get_consumers():
            asyncio.create_task(self.consume(consumer_class))

    async def get_channel(self) -> aio_pika.Channel:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def consume(self, consumer_class: Type[BaseConsumer]) -> None:
        channel = await self.get_channel()
        consumer = consumer_class()

        await channel.set_qos(consumer.get_qos())
        queue = await channel.declare_queue(
            consumer.get_queue_name(),
            durable=False,
            auto_delete=False,
        )
        # 绑定队列到交换机
        exchange = await channel.get_exchange(self.config.exchange)
        await queue.bind(exchange, consumer.get_routing_key())
        Logger.get().info(f'消费队列: {consumer_class.get_queue_name()} 监听成功')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                result = await consumer.consume(message)
                if result == Result.OK:
                    await message.ack()
                elif result == Result.REJECT:
                    await message.reject(requeue=False)
                elif result == Result.RETRY:
                    await message.reject(requeue=True)

    async def publish(self, message: str, routing_key: str) -> None:
        channel = await self.get_channel()
        exchange = await channel.get_exchange(self.config.exchange)
        await exchange.publish(aio_pika.Message(body=message.encode()), routing_key=routing_key)

    async def close(self):
        if not self.config.enable:
            return
        await self.connection_pool.close()
