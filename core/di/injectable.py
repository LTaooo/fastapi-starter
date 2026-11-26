from typing import Any, TypeVar

_ClassType = TypeVar('_ClassType')
_INJECTABLE_ATTRIBUTE = '__injectable__'


def injectable(cls: type[_ClassType]) -> type[_ClassType]:
    """标记该类允许由容器反射构造。"""
    setattr(cls, _INJECTABLE_ATTRIBUTE, True)
    return cls


def is_injectable(cls: type[Any]) -> bool:
    """判断类是否（含继承）带 injectable 标记。"""
    return bool(getattr(cls, _INJECTABLE_ATTRIBUTE, False))
