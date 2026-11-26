from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

from config.env import ENV_FILES


class AppEnvEnum(str, Enum):
    DEV = 'dev'
    PROD = 'prod'
    TEST = 'test'


class AppConfig(BaseSettings):
    """应用基础配置；字段别名即环境变量名，应用级用大写加下划线，分组配置用小写加点号。"""

    model_config = SettingsConfigDict(env_file=ENV_FILES, env_file_encoding='utf-8', extra='ignore')
    app_env: AppEnvEnum = Field(description='应用环境', default=AppEnvEnum.DEV, alias='APP_ENV')
    app_name: str = Field(description='应用名称', default='fastapi-starter', alias='APP_NAME')
    app_debug: bool = Field(description='是否开启调试模式', default=False, alias='APP_DEBUG')
    app_workers: int = Field(description='工作进程数', default=1, ge=1, alias='APP_WORKERS')
    app_host: str = Field(description='主机地址', default='0.0.0.0', alias='APP_HOST')
    app_port: int = Field(description='端口号', default=8000, alias='APP_PORT')
    app_root_path: str = Field(description='根路径', default='', alias='APP_ROOT_PATH')
    docs_path: str = Field(description='文档页面路径', default='/docs', pattern=r'^/[^?#]*$', alias='docs.path')
    docs_username: str = Field(description='文档访问用户名，与密码同时配置时启用认证', default='', alias='docs.username')
    docs_password: SecretStr = Field(description='文档访问密码，与用户名同时配置时启用认证', default=SecretStr(''), alias='docs.password')

    def is_prod(self) -> bool:
        return self.app_env == AppEnvEnum.PROD

    def is_dev(self) -> bool:
        return self.app_env == AppEnvEnum.DEV

    def is_prod_or_test(self) -> bool:
        return self.app_env == AppEnvEnum.PROD or self.app_env == AppEnvEnum.TEST

    def is_docs_enabled(self) -> bool:
        """判断是否注册文档与 Schema 路由；生产环境须同时配置有效的用户名和密码。"""
        return not self.is_prod() or bool(self.docs_username.strip() and self.docs_password.get_secret_value().strip())
