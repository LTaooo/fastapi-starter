import pytest

from app.queues.demo_queue import DemoConsumer
from config.rabbitmq_config import RabbitMQConfig
from core.config import Config
from core.rabbitmq.rabbitmq import RabbitMQ
from core.util.datetime import DateTime

pytestmark = pytest.mark.skipif(not Config.get(RabbitMQConfig).enable, reason='RabbitMQ未启用')


async def test_push_demo_message():
    rabbitmq = RabbitMQ()
    await rabbitmq.connect()

    await rabbitmq.publish(DateTime.datetime(), DemoConsumer.get_routing_key())

    await rabbitmq.close()
