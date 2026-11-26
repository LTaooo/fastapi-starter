"""验证容器图的构造约束：整张图可构造，且标记类不自实例化协作对象。

被测类由扫描标记得到，不维护清单；新增带标记的类会自动纳入。

已知局限：本测试只遍历带标记的类，因此「某个类漏加标记、且仅经 inject() 的端点引用」发现不了——
它不在扫描结果里，也没有任何带标记的类依赖它。该情形目前仅由端点测试间接覆盖，漏检时会在首次请求抛 TypeError。
"""

import ast
import dataclasses
import enum
import importlib
import inspect
import pathlib
import pkgutil
from collections.abc import Iterator
from types import ModuleType

import pytest
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from core.config import Config
from core.di.container import Container
from core.di.injectable import is_injectable

_SCANNED_PACKAGES = ('app', 'config')


def _imported_modules() -> Iterator[ModuleType]:
    """逐个导入被测包内的模块，供类收集与标记扫描共用。"""
    for package_name in _SCANNED_PACKAGES:
        package = importlib.import_module(package_name)
        for module_info in pkgutil.walk_packages(package.__path__, f'{package_name}.'):
            yield importlib.import_module(module_info.name)


def _repo_classes() -> dict[str, type]:
    """收集被测包内定义的类，按类名索引。"""
    classes: dict[str, type] = {}
    for module in _imported_modules():
        for _, member in inspect.getmembers(module, inspect.isclass):
            if member.__module__.startswith(_SCANNED_PACKAGES):
                classes.setdefault(member.__name__, member)
    return classes


def _value_object_names() -> set[str]:
    """值对象（pydantic 模型、数据类、枚举）是数据而非协作者，允许被类自身构造为状态。"""
    return {name for name, member in _repo_classes().items() if issubclass(member, (BaseModel, enum.Enum)) or dataclasses.is_dataclass(member)}


def _marked_classes() -> list[type]:
    """返回被测包内全部带 injectable 标记的类，按类型去重。"""
    found: dict[type, None] = {}
    for module in _imported_modules():
        for _, member in inspect.getmembers(module, inspect.isclass):
            if is_injectable(member):
                found[member] = None
    return list(found)


def _marked_class_definitions() -> list[tuple[pathlib.Path, ast.ClassDef]]:
    """按源码顺序列出被测包内所有带 injectable 装饰器的类定义。"""
    definitions: list[tuple[pathlib.Path, ast.ClassDef]] = []
    for package_name in _SCANNED_PACKAGES:
        for path in sorted(pathlib.Path(package_name).rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and any(
                    isinstance(decorator, ast.Name) and decorator.id == 'injectable' for decorator in node.decorator_list
                ):
                    definitions.append((path, node))
    return definitions


def _self_attribute_names(statement: ast.Assign | ast.AnnAssign) -> list[str]:
    """返回赋值语句写入的 self 属性名。"""
    targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
    return [target.attr for target in targets if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self']


def _collaborator_constructions(method: ast.FunctionDef, repo_names: set[str], value_object_names: set[str]) -> list[str]:
    """返回方法中把仓库类实例化为 self 成员的被构造类名。"""
    constructed = []
    for statement in ast.walk(method):
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        value = statement.value
        if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name):
            continue
        if value.func.id in repo_names and value.func.id not in value_object_names and _self_attribute_names(statement):
            constructed.append(value.func.id)
    return constructed


@pytest.fixture
def graph_container(monkeypatch) -> Container:
    """隔离注册表与配置缓存，并为图内配置类预置实例。

    预置用 model_construct，绕开环境变量读取与必填字段校验。
    """
    container = Container()
    monkeypatch.setattr(container, '_registry', {})
    monkeypatch.setattr(Config, '_configs', {})
    monkeypatch.setattr(Config, '_Config__origin_config', {})
    for managed_class in _marked_classes():
        if issubclass(managed_class, BaseSettings):
            container.set(managed_class, managed_class.model_construct())
    return container


def test_marked_classes_are_discovered(graph_container) -> None:
    """扫描确实找到了带标记的类，避免扫描失效后测试静默通过。"""
    assert _marked_classes()


def test_entire_graph_is_constructible(graph_container) -> None:
    """每个带标记的类都能被容器构造，构造期为纯内存操作。"""
    for managed_class in _marked_classes():
        assert graph_container.get(managed_class) is not None


def test_marked_classes_do_not_construct_collaborators() -> None:
    """标记类的构造函数只把注入参数赋给成员，不把协作对象实例化为成员。"""
    repo_names = set(_repo_classes())
    value_object_names = _value_object_names()
    violations = [
        f'{path}: {definition.name}.__init__ 构造了 {name}'
        for path, definition in _marked_class_definitions()
        for method in definition.body
        if isinstance(method, ast.FunctionDef) and method.name == '__init__'
        for name in _collaborator_constructions(method, repo_names, value_object_names)
    ]
    assert violations == []
