from pydantic import Field

from config.app_config import AppConfig
from config.base.base_nacos_config import BaseNacosConfig
from core.config import Config


def _generate_exchange() -> str:
    config = Config.get(AppConfig)
    return f'exchange_{config.app_name}_{config.app_env.value}'


class RabbitMQConfig(BaseNacosConfig):
    enable: bool = Field(description='是否启用RabbitMQ', default=False, alias='rabbitmq.enable')
    host: str = Field(description='RabbitMQ主机地址', default='127.0.0.1', alias='rabbitmq.host')
    port: int = Field(description='RabbitMQ端口号', default=5672, alias='rabbitmq.port')
    username: str = Field(description='RabbitMQ用户名', default='test', alias='rabbitmq.username')
    password: str = Field(description='RabbitMQ密码', default='test', alias='rabbitmq.password')
    vhost: str = Field(description='RabbitMQ虚拟主机', default='base_vhost', alias='rabbitmq.vhost')
    prefetch: int = Field(
        description='消费者默认预取数量，消费者显式指定 channel 时以显式值为准',
        default=10,
        ge=1,
        alias='rabbitmq.prefetch',
    )
    exchange: str = Field(description='RabbitMQ交换机', default_factory=_generate_exchange, alias='rabbitmq.exchange')
