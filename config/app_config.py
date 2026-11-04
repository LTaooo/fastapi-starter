from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from config.env import ENV_FILES


class AppEnvEnum(str, Enum):
    DEV = 'dev'
    PROD = 'prod'
    TEST = 'test'


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILES, env_file_encoding='utf-8', extra='ignore')
    app_env: AppEnvEnum = Field(description='应用环境', default=AppEnvEnum.DEV)
    app_name: str = Field(description='应用名称', default='fastapi-starter')
    app_debug: bool = Field(description='是否开启调试模式', default=False)
    log_file_enable: bool = Field(description='是否输出文件日志', default=True)
    workers: int = Field(description='工作进程数', default=1, ge=1)
    host: str = Field(description='主机地址', default='0.0.0.0')
    port: int = Field(description='端口号', default=8000)
    app_root_path: str = Field(description='根路径', default='')

    def is_prod(self) -> bool:
        return self.app_env == AppEnvEnum.PROD

    def is_dev(self) -> bool:
        return self.app_env == AppEnvEnum.DEV

    def is_prod_or_test(self) -> bool:
        return self.app_env == AppEnvEnum.PROD or self.app_env == AppEnvEnum.TEST

    # noinspection HttpUrlsUsage
    def get_bind_host(self) -> str:
        return f'http://{self.host}:{self.port}'
