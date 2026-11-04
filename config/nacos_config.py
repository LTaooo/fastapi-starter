import socket
from typing import Callable

import yaml
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from v2.nacos import RegisterInstanceParam, ConfigParam

from config.app_config import AppConfig
from config.env import ENV_FILES
from core.config import Config
from core.logger import Logger
from core.util.helper import Helper


class NacosListenerConfig(BaseModel):
    data_id: str = Field(description='数据ID')
    listener: Callable = Field(description='监听器')


async def _config_listener(tenant: str, group: str, data_id: str, content: str):
    """
    nacos配置监听器

    参数顺序固定为 (tenant, group, data_id, content)，不可调整。
    """
    data = yaml.safe_load(content or '')
    if not isinstance(data, dict):
        Logger.get().warning(f'Nacos配置格式错误, 已忽略: {data_id}')
        return
    Config().update_config(data)
    Logger.get().info(f'Nacos配置已刷新: {data_id}')


_app_config = Config.get(AppConfig)


class NacosConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILES, env_file_encoding='utf-8', extra='ignore')
    enable: bool = Field(description='是否启用Nacos', alias='NACOS_ENABLE', default=False)
    register_ip: str = Field(description='服务注册IP, 为空时自动获取本机IP', alias='NACOS_REGISTER_IP', default='')
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
                ip=self.get_register_ip(),
                port=_app_config.port,
                group_name=self.group,
                weight=1,
                ephemeral=True,
            )
        ]

    def get_register_ip(self) -> str:
        if self.register_ip:
            return self.register_ip
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(('8.8.8.8', 80))
                return sock.getsockname()[0]
        except OSError as e:
            raise RuntimeError('无法自动获取本机IP, 请配置 NACOS_REGISTER_IP') from e

    @staticmethod
    def get_listener_data() -> list[NacosListenerConfig]:
        return [NacosListenerConfig(data_id=f'{_app_config.app_name}-{_app_config.app_env.value}.yaml', listener=_config_listener)]

    def get_config_data(self) -> ConfigParam:
        return ConfigParam(data_id=f'{_app_config.app_name}-{_app_config.app_env.value}.yaml', group=self.group, type='yaml')

    @staticmethod
    def get_log_dir() -> str:
        return Helper.with_root_path(['logs', 'nacos', 'app.log'])

    @staticmethod
    def get_cache_dir() -> str:
        return Helper.with_root_path(['runtime', 'nacos'])
