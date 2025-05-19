from dotenv import load_dotenv
from typing import Type, TypeVar, Generic
from pydantic import BaseModel

from config.base.base_nacos_config import BaseNacosConfig

load_dotenv()
_T = TypeVar('_T', bound=BaseModel)


class Config(Generic[_T]):
    __origin_config: dict = {}
    _configs: dict[str, _T] = {}

    @classmethod
    def get(cls, config_class: Type[_T]) -> _T:
        key = config_class.__name__
        if cls._configs.get(key) is None:
            cls._configs[key] = cls.__get(config_class)
        return cls._configs[key]

    @classmethod
    def __get(cls, config_class: Type[_T]) -> _T:
        if issubclass(config_class, BaseNacosConfig):
            return config_class(**cls.__flatten_dict(cls.__origin_config))

        return config_class()

    @classmethod
    def __flatten_dict(cls, d: dict, sep: str = '.') -> dict:
        """将嵌套字典扁平化，例如 {'a': {'b': 1}} -> {'a.b': 1}"""
        items = {}
        for k, v in d.items():
            for k1, v1 in v.items():
                items[f'{k}{sep}{k1}' if k else k1] = v1
        return items

    @classmethod
    def update_config(cls, data: dict):
        cls.__origin_config = data
        cls._configs = {}
