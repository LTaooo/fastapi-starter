from typing import Type, TypeVar, ClassVar, cast
from pydantic import BaseModel

from config.base.base_nacos_config import BaseNacosConfig

_T = TypeVar('_T', bound=BaseModel)


class Config:
    __origin_config: ClassVar[dict] = {}
    _configs: ClassVar[dict[type[BaseModel], BaseModel]] = {}

    @classmethod
    def get(cls, config_class: Type[_T]) -> _T:
        """按配置类型缓存实例，隔离不同模块中同名的配置类。"""
        instance = cls._configs.get(config_class)
        if instance is None:
            instance = cls.__get(config_class)
            cls._configs[config_class] = instance
        return cast(_T, instance)

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
