from functools import lru_cache

from pydantic_settings import BaseSettings

from typing import Type, TypeVar
from dotenv import load_dotenv

load_dotenv()
T = TypeVar('T', bound=BaseSettings)


class Config:
    @classmethod
    def get(cls, config_class: Type[T]) -> T:
        return cls._get_config(config_class)

    @classmethod
    @lru_cache(maxsize=128)
    def _get_config(cls, config_class: Type[T]) -> T:
        return config_class()
