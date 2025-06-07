from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppEnvEnum(str, Enum):
    DEV = 'dev'
    PROD = 'prod'
    TEST = 'test'


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    app_name: str = Field(description='应用名称', default='fastapi-template', alias='SERVICE_NAME')
    app_debug: bool = Field(description='是否开启调试模式', default=False, alias='APP_DEBUG')
    app_env: AppEnvEnum = Field(description='应用环境', default=AppEnvEnum.DEV, alias='ENV')
    workers: int = Field(description='工作进程数', default=8, alias='WORKERS')
    host: str = Field(description='主机地址', default='0.0.0.0', alias='HOST')
    port: int = Field(description='端口号', default=8001, alias='PORT')

    def is_prod(self) -> bool:
        return self.app_env == AppEnvEnum.PROD

    def is_dev(self) -> bool:
        return self.app_env == AppEnvEnum.DEV

    def is_prod_or_test(self) -> bool:
        return self.app_env == AppEnvEnum.PROD or self.app_env == AppEnvEnum.TEST
