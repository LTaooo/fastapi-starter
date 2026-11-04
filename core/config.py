from typing import Type, TypeVar, ClassVar
from pydantic import BaseModel

from config.base.base_nacos_config import BaseNacosConfig

_T = TypeVar('_T', bound=BaseModel)


class Config:
    __origin_config: ClassVar[dict] = {}
    _configs: ClassVar[dict] = {}

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
            # 顶层非字典值无法映射为 "段.字段" 配置项, 跳过
            if not isinstance(v, dict):
                continue
            for k1, v1 in v.items():
                items[f'{k}{sep}{k1}' if k else k1] = v1
        return items

    @classmethod
    def update_config(cls, data: dict):
        # Nacos 内容可能解析为 list/scalar, 非映射配置直接忽略
        if not isinstance(data, dict):
            return
        cls.__origin_config = data
        cls._configs = {}
