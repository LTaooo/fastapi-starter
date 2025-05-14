import tomllib
from typing import Callable
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from v2.nacos import RegisterInstanceParam

from config.app_config import AppConfig
from core.config import Config


class NacosListenerConfig(BaseModel):
    data_id: str = Field(description='数据ID')
    listener: Callable = Field(description='监听器')


async def _config_listener(tenant: str, data_id: str, group: str, content: str):
    """
    nacos配置监听器
    """
    content_dict = tomllib.loads(content)
    print(content_dict)


class NacosConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    enable: bool = Field(description='是否启用Nacos', alias='NACOS_ENABLE', default=False)
    server_addresses: str = Field(description='Nacos服务器地址', alias='NACOS_SERVER_ADDRESSES', default='127.0.0.1:8848')
    namespace: str = Field(description='Nacos命名空间', alias='NACOS_NAMESPACE', default='dev')
    group: str = Field(description='Nacos组', alias='NACOS_GROUP', default='DEFAULT_GROUP')
    username: str = Field(description='Nacos用户名', alias='NACOS_USERNAME', default='dev')
    password: str = Field(description='Nacos密码', alias='NACOS_PASSWORD', default='dev')
    log_level: str = Field(description='Nacos日志级别', alias='NACOS_LOG_LEVEL', default='ERROR')
    log_dir: str = Field(description='Nacos日志目录', alias='NACOS_LOG_DIR', default='logs/nacos_naming_client.log')

    def get_services_data(self) -> list[RegisterInstanceParam]:
        _app_config = Config.get(AppConfig)
        return [
            RegisterInstanceParam(
                service_name=_app_config.app_name,
                ip='127.0.0.1',
                port=_app_config.port,
                group_name=self.group,
                weight=1,
                ephemeral=True,
            )
        ]

    @staticmethod
    def get_listener_data() -> list[NacosListenerConfig]:
        return [NacosListenerConfig(data_id='fast-api-template-dev.toml', listener=_config_listener)]
