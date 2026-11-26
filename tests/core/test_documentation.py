from typing import Any
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

with patch.dict('os.environ', {'APP_ENV': 'test'}):
    from config.app_config import AppConfig, AppEnvEnum
    from core import documentation
    from core.exception.handle import exception_handle


class DocumentationTestConfig(AppConfig):
    model_config = SettingsConfigDict(env_file=None)


def create_config(app_env: AppEnvEnum, username: str = '', password: str = '') -> DocumentationTestConfig:
    """构造隔离配置；键使用字段别名，与 .env 中的写法一致。"""
    overrides: dict[str, Any] = {'APP_ENV': app_env, 'docs.username': username, 'docs.password': SecretStr(password)}
    return DocumentationTestConfig(**overrides)


def create_application(username: str = '', password: str = '', app_env: AppEnvEnum = AppEnvEnum.TEST) -> FastAPI:
    """使用假凭据与真实异常处理构造隔离应用，不读取 dotenv 或连接外部服务。"""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    exception_handle.register(app)
    documentation.register(app, create_config(app_env, username, password))
    return app


@pytest.mark.parametrize('credentials', [('', ''), ('reader', ''), ('', 'test-password')])
def test_unconfigured_documentation_is_public(credentials: tuple[str, str]) -> None:
    """未配置完整凭据时，非生产环境的文档页面和 Schema 均可直接访问。"""
    with TestClient(create_application(*credentials)) as client:
        assert client.get('/docs').status_code == 200
        assert client.get('/openapi.json').status_code == 200


def test_configured_documentation_requires_authentication() -> None:
    """启用认证后拒绝缺失、错误或畸形凭据，并保留浏览器登录挑战。"""
    with TestClient(create_application('reader', 'test-password')) as client:
        for path in ('/docs', '/openapi.json'):
            responses = [
                client.get(path),
                client.get(path, auth=('reader', 'wrong-password')),
                client.get(path, headers={'Authorization': 'Basic !!!'}),
            ]
            for response in responses:
                assert response.status_code == 401
                assert response.headers['www-authenticate'] == 'Basic realm="API docs"'


def test_correct_credentials_allow_documentation_access() -> None:
    """正确凭据可取得 Scalar 页面与 OpenAPI Schema。"""
    with TestClient(create_application('reader', 'test-password')) as client:
        page = client.get('/docs', auth=('reader', 'test-password'))
        assert page.status_code == 200
        assert 'Scalar.createApiReference' in page.text
        schema = client.get('/openapi.json', auth=('reader', 'test-password'))
        assert schema.status_code == 200
        assert 'openapi' in schema.json()


@pytest.mark.parametrize('credentials', [('', ''), ('reader', ''), ('', 'test-password')])
def test_production_without_full_credentials_does_not_serve_documentation(credentials: tuple[str, str]) -> None:
    """生产环境只配一半凭据时不得注册文档，避免 Schema 与页面被公开。"""
    with TestClient(create_application(*credentials, app_env=AppEnvEnum.PROD)) as client:
        assert 'Scalar.createApiReference' not in client.get('/docs').text


def test_production_with_credentials_serves_authenticated_documentation() -> None:
    """生产环境配置完整凭据后注册文档，并要求通过认证才能访问。"""
    with TestClient(create_application('reader', 'test-password', app_env=AppEnvEnum.PROD)) as client:
        assert client.get('/docs').status_code == 401
        page = client.get('/docs', auth=('reader', 'test-password'))
        assert page.status_code == 200
        assert 'Scalar.createApiReference' in page.text


@pytest.mark.parametrize('app_env', [AppEnvEnum.DEV, AppEnvEnum.TEST, AppEnvEnum.PROD])
def test_is_docs_enabled_requires_credentials_in_production(app_env: AppEnvEnum) -> None:
    """文档只在非生产环境或生产环境配置完整凭据时启用。"""
    assert create_config(app_env).is_docs_enabled() is (app_env is not AppEnvEnum.PROD)
    assert create_config(app_env, 'reader', 'test-password').is_docs_enabled() is True
