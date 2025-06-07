from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig


class RedisConfig(BaseNacosConfig):
    host: str = Field(description='Redis主机地址', default='localhost1', alias='redis.host')
    port: int = Field(description='Redis端口号', default=6379, alias='redis.port')
    db: int = Field(description='Redis数据库', default=0, alias='redis.db')
    password: str = Field(description='Redis密码', default='', alias='redis.password')
    connection_pool: int = Field(description='Redis连接池', default=10, alias='redis.connection_pool')
