from collections.abc import Awaitable, Callable
from secrets import compare_digest

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic
from scalar_fastapi import AgentScalarConfig, get_scalar_api_reference
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.app_config import AppConfig


def _authentication(username: str, password: str) -> Callable[[Request], Awaitable[None]]:
    """创建文档认证依赖，保留 HTTP 401 与浏览器登录挑战，不经过业务异常转换。"""
    security = HTTPBasic(realm='API docs')

    async def authenticate(request: Request) -> None:
        """解析 Basic 凭据并以恒定时间比较，所有认证失败使用相同响应。"""
        unauthorized = StarletteHTTPException(
            status_code=401,
            detail='Invalid documentation credentials',
            headers={'WWW-Authenticate': 'Basic realm="API docs"'},
        )
        try:
            credentials = await security(request)
        except HTTPException:
            # 业务处理器会将 FastAPI HTTPException 转成 200，文档必须保留认证状态码。
            raise unauthorized from None
        if credentials is None:
            raise unauthorized
        username_matches = compare_digest(credentials.username.encode('utf-8'), username.encode('utf-8'))
        password_matches = compare_digest(credentials.password.encode('utf-8'), password.encode('utf-8'))
        if not (username_matches and password_matches):
            raise unauthorized

    return authenticate


def register(app: FastAPI, config: AppConfig) -> None:
    """按配置路径注册文档；未启用时（生产环境缺凭据）不注册任何文档路由。"""
    if not config.is_docs_enabled():
        return

    username = config.docs_username
    password = config.docs_password.get_secret_value()
    dependencies = [Depends(_authentication(username, password))] if username.strip() and password.strip() else []
    openapi_url = '/openapi.json'

    @app.get(config.docs_path, include_in_schema=False, dependencies=dependencies)
    async def documentation(request: Request) -> HTMLResponse:
        """返回同源 Scalar 页面，浏览器复用 Basic 认证加载 Schema。"""
        root_path = request.scope.get('root_path', '').rstrip('/')
        return get_scalar_api_reference(
            openapi_url=f'{root_path}{openapi_url}',
            title=app.title,
            telemetry=False,
            agent=AgentScalarConfig(disabled=True),
            persist_auth=False,
            with_default_fonts=False,
        )

    @app.get(openapi_url, include_in_schema=False, dependencies=dependencies)
    async def schema(request: Request) -> JSONResponse:
        """返回现有定制 Schema，保留反向代理前缀的服务器地址。"""
        root_path = request.scope.get('root_path', '').rstrip('/')
        server_urls = {server.get('url') for server in app.servers}
        if root_path and app.root_path_in_servers and root_path not in server_urls:
            app.servers.insert(0, {'url': root_path})
            app.openapi_schema = None
        return JSONResponse(app.openapi())
