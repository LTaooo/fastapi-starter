from abc import ABC
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseNacosConfig(ABC, BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
