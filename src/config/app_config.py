from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppEnvEnum(str, Enum):
    DEV = 'dev'
    PROD = 'prod'
    TEST = 'test'


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    app_env: AppEnvEnum = Field(description='应用环境', default=AppEnvEnum.DEV)
    app_name: str = Field(description='应用名称', default='fastapi-template')
    app_debug: bool = Field(description='是否开启调试模式', default=False)

    def is_prod(self) -> bool:
        return self.app_env == AppEnvEnum.PROD

    def is_dev(self) -> bool:
        return self.app_env == AppEnvEnum.DEV
