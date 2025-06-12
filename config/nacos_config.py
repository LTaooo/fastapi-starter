import tomllib
from typing import Callable
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from v2.nacos import RegisterInstanceParam, ConfigParam

from config.app_config import AppConfig
from core.config import Config
from core.util.helper import Helper


class NacosListenerConfig(BaseModel):
    data_id: str = Field(description='数据ID')
    listener: Callable = Field(description='监听器')


async def _config_listener(tenant: str, data_id: str, group: str, content: str):
    """
    nacos配置监听器
    """
    content_dict = tomllib.loads(content)
    print(content_dict)


_app_config = Config.get(AppConfig)


class NacosConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    enable: bool = Field(description='是否启用Nacos', alias='NACOS_ENABLE', default=False)
    server_addresses: str = Field(description='Nacos服务器地址', alias='NACOS_SERVER_ADDRESSES', default='127.0.0.1:8848')
    namespace: str = Field(description='Nacos命名空间', alias='NACOS_NAMESPACE', default='dev')
    group: str = Field(description='Nacos组', alias='NACOS_GROUP', default='DEFAULT_GROUP')
    username: str = Field(description='Nacos用户名', alias='NACOS_USERNAME', default='dev')
    password: str = Field(description='Nacos密码', alias='NACOS_PASSWORD', default='dev')
    log_level: str = Field(description='Nacos日志级别', alias='NACOS_LOG_LEVEL', default='ERROR')

    def get_services_data(self) -> list[RegisterInstanceParam]:
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
        return [NacosListenerConfig(data_id=f'{_app_config.app_name}-{_app_config.app_env.value}.yml', listener=_config_listener)]

    def get_config_data(self) -> ConfigParam:
        return ConfigParam(data_id=f'{_app_config.app_name}-{_app_config.app_env.value}.yaml', group=self.group, type='yaml')

    @staticmethod
    def get_log_dir() -> str:
        return Helper.with_root_path(['logs', 'nacos', 'app.log'])

    @staticmethod
    def get_cache_dir() -> str:
        return Helper.with_root_path(['runtime', 'nacos'])
