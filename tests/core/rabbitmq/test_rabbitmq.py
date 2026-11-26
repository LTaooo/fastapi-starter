from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from faststream.middlewares import AckPolicy
from faststream.rabbit import TestRabbitBroker

with patch.dict('os.environ', {'APP_ENV': 'test'}):
    from app.queues.demo_queue import DemoMessage, DemoQueue
    from config.app_config import AppConfig, AppEnvEnum
    from config.queue_config import QueueConfig
    from config.rabbitmq_config import RabbitMQConfig
    from core.config import Config
    from core.rabbitmq import RabbitMQ, build_broker, build_exchange, consumer, get_consumers, queue_interface


@pytest.fixture
def queue_configuration(monkeypatch: pytest.MonkeyPatch) -> RabbitMQConfig:
    """隔离配置缓存、消费者表与注册状态，不读取 dotenv 或连接外部服务。"""
    app_config = AppConfig.model_construct(app_env=AppEnvEnum.DEV, app_name='queue-test')
    rabbitmq_config = RabbitMQConfig.model_construct(exchange='queue-test-exchange')
    monkeypatch.setattr(Config, '_configs', {AppConfig: app_config, RabbitMQConfig: rabbitmq_config})
    monkeypatch.setattr(consumer, '_consumers', [])
    monkeypatch.setattr(queue_interface, '_registered_queue_types', set())
    return rabbitmq_config


async def test_demo_queue_consumes(queue_configuration: RabbitMQConfig) -> None:
    """内存 broker 根据具体消费方法的注解将字典转换为演示消息。"""
    QueueConfig.register()
    broker = build_broker(queue_configuration)
    logger = MagicMock()

    async with TestRabbitBroker(broker) as test_broker:
        with (
            patch('app.queues.demo_queue.Logger.get', return_value=logger),
            patch('app.queues.demo_queue.asyncio', SimpleNamespace(sleep=AsyncMock())),
        ):
            await test_broker.publish(
                {'content': 'hello'},
                exchange=build_exchange(queue_configuration),
                routing_key=DemoQueue().queue.routing_key,
            )

    logger.info.assert_any_call('接收到消息 content={}', 'hello')
    logger.info.assert_any_call('消息处理完成 content={}', 'hello')


async def test_demo_queue_publishes(queue_configuration: RabbitMQConfig) -> None:
    """继承的发布方法使用具体队列声明中的路由键。"""
    instance = DemoQueue()
    message = DemoMessage(content='hello')
    with patch.object(RabbitMQ, 'publish', new_callable=AsyncMock) as publish:
        await instance.publish(message)

    publish.assert_awaited_once_with(message, routing_key=instance.queue.routing_key)


def test_registration_is_idempotent(queue_configuration: RabbitMQConfig) -> None:
    """重复配置只登记一个消费者，队列类提供持久化与消费策略。"""
    QueueConfig.register()
    QueueConfig.register()

    consumers = get_consumers()
    assert len(consumers) == 1
    specification = consumers[0]
    assert specification.queue.name == 'queue-test_demo'
    assert specification.queue.routing_key == 'queue-test_demo'
    assert specification.queue.durable is True
    assert specification.ack_policy == AckPolicy.REJECT_ON_ERROR
    assert specification.channel is not None
    assert specification.channel.prefetch_count == 1


def test_registration_skips_nondevelopment(queue_configuration: RabbitMQConfig) -> None:
    """具体队列的启用规则决定是否注册，禁用后仍可在允许时重试。"""
    Config.get(AppConfig).app_env = AppEnvEnum.PROD
    QueueConfig.register()
    assert get_consumers() == ()

    Config.get(AppConfig).app_env = AppEnvEnum.DEV
    QueueConfig.register()
    assert len(get_consumers()) == 1
