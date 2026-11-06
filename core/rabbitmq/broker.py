from typing import Any
from urllib.parse import quote

from faststream.middlewares import AckPolicy
from faststream.rabbit import Channel, ExchangeType, RabbitBroker, RabbitExchange

from config.app_config import AppConfig
from config.rabbitmq_config import RabbitMQConfig
from core.config import Config
from core.logger import Logger
from core.rabbitmq.consumer import get_consumers
from core.singleton_meta import SingletonMeta


def build_exchange(config: RabbitMQConfig) -> RabbitExchange:
    """构建项目统一的 Direct 持久化交换机。"""
    return RabbitExchange(name=config.exchange, type=ExchangeType.DIRECT, durable=True)


def build_broker(config: RabbitMQConfig) -> RabbitBroker:
    """按当前配置构建 broker，并绑定已登记的消费者。"""
    broker = RabbitBroker(
        url=_build_url(config),
        timeout=3.0,
        fail_fast=True,
        reconnect_interval=5.0,
        graceful_timeout=15.0,
        ack_policy=AckPolicy.REJECT_ON_ERROR,
        app_id=Config.get(AppConfig).app_name,
    )
    exchange = build_exchange(config)
    for consumer in get_consumers():
        broker.subscriber(
            consumer.queue,
            exchange,
            ack_policy=consumer.ack_policy,
            channel=consumer.channel or Channel(prefetch_count=config.prefetch),
        )(consumer.handler)
    return broker


def _build_url(config: RabbitMQConfig) -> str:
    """生成 AMQP URL；用户名、密码和 vhost 均做 URL 转义。"""
    return (
        f'amqp://{quote(config.username, safe="")}:{quote(config.password, safe="")}'
        f'@{config.host}:{config.port}/{quote(config.vhost, safe="")}'
    )


class RabbitMQ(metaclass=SingletonMeta):
    """RabbitMQ broker 生命周期与消息发布入口。"""

    def __init__(self) -> None:
        self._broker: RabbitBroker | None = None
        self._started = False

    def is_enable(self) -> bool:
        return Config.get(RabbitMQConfig).enable

    def _get_broker(self) -> RabbitBroker:
        if self._broker is None:
            self._broker = build_broker(Config.get(RabbitMQConfig))
        return self._broker

    async def start(self) -> None:
        """启动 broker；消费者注册表在此时一次性绑定，调用前必须完成全部 register_consumer 调用。"""
        if not self.is_enable() or self._started:
            return
        await self._get_broker().start()
        self._started = True
        names = ', '.join(consumer.queue.name for consumer in get_consumers()) or '无'
        Logger.get().info(f'RabbitMQ连接成功, 消费者: {names}')

    async def stop(self) -> None:
        broker = self._broker
        if broker is None:
            return
        self._broker = None
        self._started = False
        try:
            await broker.stop()
        except Exception as e:
            Logger.get().error(f'RabbitMQ关闭失败: {e}')

    async def publish(self, message: Any, routing_key: str, exchange: RabbitExchange | str | None = None) -> None:
        """发布消息；未启用时跳过，未启动时抛出异常。"""
        config = Config.get(RabbitMQConfig)
        if not config.enable:
            Logger.get().warning('RabbitMQ未启用, 跳过消息发布')
            return
        if not self._started:
            raise RuntimeError('RabbitMQ未启动')
        await self._get_broker().publish(
            message,
            exchange=exchange or build_exchange(config),
            routing_key=routing_key,
            persist=True,
        )
