from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.base.base_nacos_config import BaseNacosConfig
from core.config import Config
from core.di.container import Container
from core.di.injectable import injectable


@injectable
class ExampleRepository:
    """无需构造参数的仓库。"""


@injectable
class ExampleService:
    """依赖仓库的服务。"""

    def __init__(self, repository: ExampleRepository) -> None:
        """保存注入的仓库。"""
        self.repository = repository


@injectable
class ExampleController:
    """递归依赖服务的控制器。"""

    def __init__(self, service: ExampleService) -> None:
        """保存注入的服务。"""
        self.service = service


@injectable
class LocalSettings(BaseSettings):
    """仅从指定环境变量获取的本地配置。"""

    model_config = SettingsConfigDict(env_file=None)
    value: str = Field(default='local', validation_alias='CONTAINER_TEST_VALUE')


@injectable
class RemoteSettings(BaseNacosConfig):
    """从远程配置字典获取的配置。"""

    model_config = SettingsConfigDict(env_file=None, extra='ignore')
    value: str = Field(default='default', alias='container_test.value')


class InheritedRemoteSettings(RemoteSettings):
    """间接继承配置基类。"""


@injectable
class ConfiguredService:
    """同时依赖本地、远程配置与普通服务。"""

    def __init__(self, local: LocalSettings, remote: InheritedRemoteSettings, service: ExampleService) -> None:
        """保存不同来源的配置与普通依赖。"""
        self.local = local
        self.remote = remote
        self.service = service


@injectable
class ForwardService:
    """使用字符串注解的服务。"""

    def __init__(self, repository: 'ExampleRepository') -> None:
        """保存前向注解解析出的仓库。"""
        self.repository = repository


class UnmarkedRepository:
    """未带标记的仓库，用于验证容器拒绝构造。"""


@injectable
class NestedUnmarkedService:
    """依赖未标记类的服务，用于验证错误同时指明所属参数。"""

    def __init__(self, repository: UnmarkedRepository) -> None:
        """保存注入的仓库。"""
        self.repository = repository


class UnmarkedSettings(BaseSettings):
    """未带标记的配置类，用于验证标记检查先于配置分支。"""

    model_config = SettingsConfigDict(env_file=None)
    value: str = Field(default='unmarked')


@pytest.fixture(autouse=True)
def isolated_container(monkeypatch) -> Container:
    """为每项测试隔离实例注册表、原始配置和配置缓存。"""
    container = Container()
    monkeypatch.setattr(container, '_registry', {})
    monkeypatch.setattr(Config, '_configs', {})
    monkeypatch.setattr(Config, '_Config__origin_config', {})
    monkeypatch.delenv('CONTAINER_TEST_VALUE', raising=False)
    return container


def test_manual_registration(isolated_container):
    """显式注册的实例优先于自动构造。"""
    repository = ExampleRepository()
    isolated_container.set(ExampleRepository, repository)
    controller = isolated_container.get(ExampleController)
    assert controller.service.repository is repository


def test_auto_resolve(isolated_container):
    """独立的空容器递归创建依赖并重复返回同一实例。"""
    controller = isolated_container.get(ExampleController)
    assert isinstance(controller.service.repository, ExampleRepository)
    assert isolated_container.get(ExampleController) is controller
    assert isolated_container.get(ExampleService) is controller.service


def test_direct_settings_use_config_provider(isolated_container, monkeypatch):
    """直接获取 BaseSettings 时沿用 Config 的环境变量加载和缓存。"""
    monkeypatch.setenv('CONTAINER_TEST_VALUE', 'environment')
    settings = isolated_container.get(LocalSettings)
    assert settings.value == 'environment'
    assert settings is Config.get(LocalSettings)
    assert isolated_container.get(LocalSettings) is settings


def test_recursive_settings_injection(isolated_container, monkeypatch):
    """递归注入普通配置和间接继承的 Nacos 配置。"""
    monkeypatch.setenv('CONTAINER_TEST_VALUE', 'environment')
    Config.update_config({'container_test': {'value': 'remote'}})
    service = isolated_container.get(ConfiguredService)
    assert service.local.value == 'environment'
    assert service.remote.value == 'remote'
    assert service.remote is isolated_container.get(InheritedRemoteSettings)
    assert service.service is isolated_container.get(ExampleService)


def test_registered_settings_override_provider(isolated_container, monkeypatch):
    """配置也优先使用显式注册的实例，不调用配置提供者。"""
    settings = LocalSettings.model_construct(value='registered')

    def unexpected_load(_config_class):
        """拒绝访问配置加载路径。"""
        pytest.fail('registered configuration must not be loaded again')

    isolated_container.set(LocalSettings, settings)
    monkeypatch.setattr(Config, 'get', unexpected_load)
    assert isolated_container.get(LocalSettings) is settings


def test_defaults_are_preserved(isolated_container):
    """默认参数不注入或求值注解，必填依赖仍正常解析。"""

    @injectable
    class DefaultsService:
        """包含可选依赖、基础类型及未注解默认参数。"""

        def __init__(self, service: ExampleService, repository: ExampleRepository | None = None, limit: int = 3, label='default') -> None:
            """保存必填依赖并保留构造默认值。"""
            self.service = service
            self.repository = repository
            self.limit = limit
            self.label = label

    DefaultsService.__init__.__annotations__['label'] = 'OnlyImportedForTypeChecking'
    isolated_container.set(ExampleRepository, ExampleRepository())
    resolved = isolated_container.get(DefaultsService)
    assert resolved.service is isolated_container.get(ExampleService)
    assert resolved.repository is None
    assert resolved.limit == 3
    assert resolved.label == 'default'


def test_forward_annotations(isolated_container):
    """字符串注解解析为对应的实际类型。"""
    service = isolated_container.get(ForwardService)
    assert service.repository is isolated_container.get(ExampleRepository)


def test_missing_required_annotation(isolated_container):
    """必填参数未注解时错误包含构造位置。"""

    @injectable
    class MissingAnnotation:
        """包含缺少注解的必填参数。"""

        def __init__(self, repository):
            """接收无法自动识别类型的依赖。"""
            self.repository = repository

    with pytest.raises(TypeError, match='MissingAnnotation.repository'):
        isolated_container.get(MissingAnnotation)


def test_unresolved_forward_annotation(isolated_container):
    """无法解析的字符串注解报告所属构造函数。"""

    @injectable
    class UnresolvedAnnotation:
        """在运行时设置不可解析的注解。"""

        def __init__(self, repository):
            """接收不存在的依赖类型。"""
            self.repository = repository

    UnresolvedAnnotation.__init__.__annotations__['repository'] = 'MissingRepository'
    with pytest.raises(TypeError, match='UnresolvedAnnotation'):
        isolated_container.get(UnresolvedAnnotation)


@pytest.mark.parametrize(('dependency_type', 'registered'), [(str, 'registered'), (Path, Path('wallet-output')), (Decimal, Decimal('12.5'))])
def test_value_dependency_requires_registration(isolated_container, dependency_type, registered):
    """内建与非内建值类型都不得自动构造，显式注册后才可注入。"""

    @injectable
    class NamedService:
        """运行时设置必填参数的具体值类型。"""

        def __init__(self, name: str) -> None:
            """保存显式提供的名称。"""
            self.name = name

    NamedService.__init__.__annotations__['name'] = dependency_type
    with pytest.raises(TypeError, match='NamedService.name.*explicitly registered'):
        isolated_container.get(NamedService)
    isolated_container.set(dependency_type, registered)
    assert isolated_container.get(NamedService).name is registered


def test_same_named_settings_are_isolated(isolated_container):
    """同名配置类型分别缓存，不返回其他类型的配置实例。"""

    class OtherSettings(LocalSettings):
        """与已有配置同名但默认值不同的独立类型。"""

        value: str = 'other'

    OtherSettings.__name__ = LocalSettings.__name__
    first = isolated_container.get(LocalSettings)
    second = isolated_container.get(OtherSettings)
    assert type(first) is LocalSettings
    assert type(second) is OtherSettings
    assert first.value == 'local'
    assert second.value == 'other'
    assert Config.get(LocalSettings) is first
    assert Config.get(OtherSettings) is second


def test_union_dependency_is_rejected(isolated_container):
    """必填联合类型不自动选择某个分支。"""

    @injectable
    class UnionService:
        """包含不可直接构造的联合类型依赖。"""

        def __init__(self, repository: ExampleRepository | None) -> None:
            """声明没有默认值的可空依赖。"""
            self.repository = repository

    with pytest.raises(TypeError, match='UnionService.repository.*Unsupported dependency type'):
        isolated_container.get(UnionService)


def test_plain_model_requires_marker(isolated_container, monkeypatch):
    """普通 Pydantic DTO 不经 Config 解析，未带标记时被容器拒绝。"""

    class EmptyModel(BaseModel):
        """无必填字段的普通 DTO。"""

    def unexpected_load(_config_class):
        """拒绝将普通 DTO 当成配置加载。"""
        pytest.fail('plain models are not configuration')

    monkeypatch.setattr(Config, 'get', unexpected_load)
    with pytest.raises(TypeError, match='must be marked with @injectable: EmptyModel'):
        isolated_container.get(EmptyModel)


def test_config_update_does_not_refresh_injected_instances(isolated_container, monkeypatch):
    """配置缓存刷新不会替换容器中已有对象，重建后才使用新配置。"""
    Config.update_config({'container_test': {'value': 'initial'}})
    service = isolated_container.get(ConfiguredService)

    Config.update_config({'container_test': {'value': 'updated'}})
    assert Config.get(InheritedRemoteSettings).value == 'updated'
    assert isolated_container.get(ConfiguredService) is service
    assert isolated_container.get(InheritedRemoteSettings) is service.remote
    assert service.remote.value == 'initial'

    monkeypatch.setattr(isolated_container, '_registry', {})
    monkeypatch.setattr(Config, '_configs', {})
    restarted = isolated_container.get(ConfiguredService)
    assert restarted is not service
    assert restarted.remote.value == 'updated'


def test_marked_class_is_constructed(isolated_container):
    """带标记的类由容器构造并复用同一实例。"""
    repository = isolated_container.get(ExampleRepository)
    assert isinstance(repository, ExampleRepository)
    assert isolated_container.get(ExampleRepository) is repository


def test_unmarked_class_is_rejected(isolated_container):
    """未带标记的类被容器拒绝构造，错误指明类名。"""
    with pytest.raises(TypeError, match='must be marked with @injectable: UnmarkedRepository'):
        isolated_container.get(UnmarkedRepository)


def test_unmarked_nested_dependency_reports_owner(isolated_container):
    """未标记的嵌套依赖在错误中同时指明所属参数。"""
    with pytest.raises(TypeError, match='NestedUnmarkedService.repository.*must be marked with @injectable'):
        isolated_container.get(NestedUnmarkedService)


def test_unmarked_settings_is_rejected(isolated_container):
    """未带标记的配置类同样被拒绝，标记检查先于配置分支。"""
    with pytest.raises(TypeError, match='must be marked with @injectable: UnmarkedSettings'):
        isolated_container.get(UnmarkedSettings)


def test_registered_instance_bypasses_marker(isolated_container):
    """显式注册的实例不受标记约束。"""
    repository = UnmarkedRepository()
    isolated_container.set(UnmarkedRepository, repository)
    assert isolated_container.get(UnmarkedRepository) is repository


def test_marker_is_inherited(isolated_container):
    """子类继承父类的标记，无需重复声明。"""
    assert isinstance(isolated_container.get(InheritedRemoteSettings), InheritedRemoteSettings)
