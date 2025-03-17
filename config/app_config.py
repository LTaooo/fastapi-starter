from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    app_name: str = Field(description="应用名称", default="fastapi-template")
    app_debug: bool = Field(description="是否开启调试模式", default=False)
