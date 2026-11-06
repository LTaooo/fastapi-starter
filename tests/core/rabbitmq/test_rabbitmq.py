from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from faststream.rabbit import TestRabbitBroker

from app.queues.demo_queue import DEMO_QUEUE, DemoMessage, publish_demo
from config.rabbitmq_config import RabbitMQConfig
from core.config import Config
from core.rabbitmq import RabbitMQ, build_broker, build_exchange


async def test_consume_demo():
    broker = build_broker(Config.get(RabbitMQConfig))
    logger = MagicMock()

    async with TestRabbitBroker(broker) as test_broker:
        with (
            patch('app.queues.demo_queue.Logger.get', return_value=logger),
            patch('app.queues.demo_queue.asyncio', SimpleNamespace(sleep=AsyncMock())),
        ):
            await test_broker.publish(
                DemoMessage(content='hello'),
                exchange=build_exchange(Config.get(RabbitMQConfig)),
                routing_key=DEMO_QUEUE.routing_key,
            )

    logger.info.assert_any_call('接收到消息: hello')
    logger.info.assert_any_call('完成消息: hello')


async def test_publish_demo():
    with patch.object(RabbitMQ, 'publish', new_callable=AsyncMock) as publish:
        await publish_demo('hello')

    assert publish.await_args is not None
    (message,) = publish.await_args.args
    assert isinstance(message, DemoMessage)
    assert message.content == 'hello'
    assert publish.await_args.kwargs == {'routing_key': DEMO_QUEUE.routing_key}
