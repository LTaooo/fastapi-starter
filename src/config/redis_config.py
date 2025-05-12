from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    host: str = Field(description='Redis主机地址', default='localhost', alias='REDIS_HOST')
    port: int = Field(description='Redis端口号', default=6379, alias='REDIS_PORT')
    db: int = Field(description='Redis数据库', default=0, alias='REDIS_DB')
    password: str = Field(description='Redis密码', default='', alias='REDIS_PASSWORD')
    connection_pool: int = Field(description='Redis连接池', default=10, alias='REDIS_CONNECTION_POOL')
