from app.queues.demo_queue import DemoConsumer
from core.rabbitmq.rabbitmq import RabbitMQ
from core.util.datetime import DateTime


async def test_push_demo_message():
    rabbitmq = RabbitMQ()
    await rabbitmq.connect()

    # 发布消息
    for i in range(1):
        await rabbitmq.publish(DateTime.datetime(), DemoConsumer.get_routing_key())

    await rabbitmq.close()
