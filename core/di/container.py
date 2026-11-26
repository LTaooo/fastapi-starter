import inspect
from datetime import date, time, timedelta
from decimal import Decimal
from enum import Enum
from numbers import Number
from pathlib import PurePath
from types import SimpleNamespace
from typing import Any, TypeVar, cast, get_type_hints
from uuid import UUID

from pydantic_settings import BaseSettings

from core.config import Config
from core.di.injectable import is_injectable
from core.singleton_meta import SingletonMeta

_Instance = TypeVar('_Instance')
_VALUE_TYPES = (Number, Decimal, PurePath, date, time, timedelta, UUID, Enum)


class Container(metaclass=SingletonMeta):
    """按类型解析进程内单例；注入的配置变更需重启，不自动刷新已有依赖。"""

    def __init__(self) -> None:
        """初始化实例注册表。"""
        self._registry: dict[type, Any] = {}

    def set(self, cls: type[_Instance], instance: _Instance) -> None:
        """注册或覆盖实例；覆盖不会替换已构造对象中持有的旧依赖。"""
        self._registry[cls] = instance

    def get(self, cls: type[_Instance]) -> _Instance:
        """获取共享实例；配置依赖须在应用配置加载完成后首次解析。"""
        return self._resolve_dependency(cls)

    def _resolve_dependency(self, cls: type[_Instance]) -> _Instance:
        """优先使用注册实例；值类型须显式注册，未标记 injectable 的类拒绝构造，配置委托 Config。"""
        if not inspect.isclass(cls) or cls is Any:
            raise TypeError(f'Unsupported dependency type: {cls!r}')
        if cls in self._registry and self._registry[cls] is not None:
            return cast(_Instance, self._registry[cls])
        if cls.__module__ == 'builtins' or issubclass(cls, _VALUE_TYPES):
            raise TypeError(f'Dependency must be explicitly registered: {cls.__name__}')
        if not is_injectable(cls):
            raise TypeError(f'Dependency class must be marked with @injectable: {cls.__name__}')
        if issubclass(cls, BaseSettings):
            instance = Config.get(cls)
        else:
            instance = cls(**self._resolve_parameters(cls))
        self.set(cls, instance)
        return instance

    def _resolve_parameters(self, cls: type) -> dict[str, Any]:
        """只注入无默认值的具名参数，并为不支持的依赖补充构造位置。"""
        parameters = list(inspect.signature(cls.__init__).parameters.values())[1:]
        required = [
            parameter
            for parameter in parameters
            if parameter.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD) and parameter.default is inspect.Parameter.empty
        ]
        if not required:
            return {}
        annotations = self._resolve_required_annotations(cls, required)
        dependencies = {}
        for parameter in required:
            if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
                raise TypeError(f'Positional-only dependency is unsupported: {cls.__name__}.{parameter.name}')
            if parameter.name not in annotations:
                raise TypeError(f'Missing type annotation for {cls.__name__}.{parameter.name}')
            try:
                dependencies[parameter.name] = self._resolve_dependency(annotations[parameter.name])
            except TypeError as exc:
                raise TypeError(f'Cannot resolve {cls.__name__}.{parameter.name}: {exc}') from exc
        return dependencies

    @staticmethod
    def _resolve_required_annotations(dependency_type: type, parameters: list[inspect.Parameter]) -> dict[str, Any]:
        """只求值必填参数的注解，忽略默认参数及返回值中的类型引用。"""
        constructor = dependency_type.__init__
        annotations = getattr(constructor, '__annotations__', {})
        required = SimpleNamespace(__annotations__={parameter.name: annotations[parameter.name] for parameter in parameters if parameter.name in annotations})
        try:
            return get_type_hints(
                required,
                globalns=getattr(constructor, '__globals__', {}),
                localns={**vars(dependency_type), dependency_type.__name__: dependency_type},
            )
        except (NameError, TypeError) as exc:
            raise TypeError(f'Cannot resolve constructor annotations for {dependency_type.__name__}: {exc}') from exc
