from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.app_config import AppConfig
from core.config import Config


_app_config = Config.get(AppConfig)


class NacosService(BaseModel):
    name: str = Field(description='服务名称')
    port: int = Field(description='服务端口')
    ip: str = Field(description='服务IP', default='127.0.0.1')


class NacosConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    enable: bool = Field(description='是否启用Nacos', alias='NACOS_ENABLE', default=False)
    server_addresses: str = Field(description='Nacos服务器地址', alias='NACOS_SERVER_ADDRESSES', default='127.0.0.1:8848')
    namespace: str = Field(description='Nacos命名空间', alias='NACOS_NAMESPACE', default='dev')
    group: str = Field(description='Nacos组', alias='NACOS_GROUP', default='DEFAULT_GROUP')
    services: list[NacosService] = [NacosService(name=_app_config.app_name, port=_app_config.port)]
