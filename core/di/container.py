import inspect
from typing import Type, Any, TypeVar, cast

from core.singleton_meta import SingletonMeta

_T_CLASS = TypeVar('_T_CLASS', bound=Any)


class Container(metaclass=SingletonMeta):
    """
    依赖注入容器
    """

    def __init__(self):
        self._registry = {}

    def set(self, cls: Type[_T_CLASS], instance: _T_CLASS):
        """
        注册实例
        """
        self._registry[cls] = instance

    def get(self, cls: Type[_T_CLASS]) -> _T_CLASS:
        """
        获取实例
        """
        self._resolve_dependency(cls)
        if cls not in self._registry:
            raise KeyError(f'No instance registered for {cls}')
        return self._registry[cls]

    def _resolve_dependency(self, cls: Type[_T_CLASS]) -> _T_CLASS:
        if cls in self._registry and self._registry[cls] is not None:
            return self._registry[cls]

        # 获取构造函数参数
        init_signature = inspect.signature(cls.__init__)
        parameters: list[inspect.Parameter] = list(init_signature.parameters.values())[1:]  # 排除 self

        resolved_deps = {}
        for param in parameters:
            # 跳过 *args 和 **kwargs
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            dep_type = cast(Type[_T_CLASS], param.annotation)
            if not dep_type or dep_type is inspect.Parameter.empty:
                raise TypeError(f'Missing type annotation for {param.name} in {cls.__name__}')
            else:
                resolved_deps[param.name] = self._resolve_dependency(dep_type)

        instance = cls(**resolved_deps)
        self.set(cls, instance)
        return instance
