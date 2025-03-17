from functools import lru_cache

from pydantic_settings import BaseSettings

from typing import Type, TypeVar

T = TypeVar('T', bound=BaseSettings)


class Config:
    @classmethod
    @lru_cache(maxsize=128)
    def get(cls, config_class: Type[T]) -> T:
        return config_class()
