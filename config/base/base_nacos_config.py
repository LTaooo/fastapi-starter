from abc import ABC
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.env import ENV_FILES


class BaseNacosConfig(ABC, BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILES, env_file_encoding='utf-8', extra='ignore')
