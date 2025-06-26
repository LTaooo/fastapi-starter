from typing import Type

from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig
from core.config import Config
from config.app_config import AppConfig
from core.rabbitmq.base_consumer import BaseConsumer


def _generate_exchange():
    return f'exchange_{Config().get(AppConfig).app_name}'


class RabbitMQConfig(BaseNacosConfig):
    enable: bool = Field(description='是否启用RabbitMQ', default=False, alias='rabbitmq.enable')
    host: str = Field(description='RabbitMQ主机地址', default='127.0.0.1', alias='rabbitmq.host')
    port: int = Field(description='RabbitMQ端口号', default=5672, alias='rabbitmq.port')
    username: str = Field(description='RabbitMQ用户名', default='test', alias='rabbitmq.username')
    password: str = Field(description='RabbitMQ密码', default='test', alias='rabbitmq.password')
    vhost: str = Field(description='RabbitMQ虚拟主机', default='base_vhost', alias='rabbitmq.vhost')
    connection_pool: int = Field(description='RabbitMQ连接池', default=10, alias='rabbitmq.connection_pool')
    exchange: str = Field(description='RabbitMQ交换机', default_factory=_generate_exchange, alias='rabbitmq.exchange')

    @staticmethod
    def get_consumers() -> list[Type[BaseConsumer]]:
        return []
