from fastapi import FastAPI
from fastmcp import FastMCP

from config.app_config import AppConfig
from core.config import Config
from core.exception.handle.exception_handle import ExceptionHandler
from core.lifespan import lifespan

# from core.mcp import mcp
from core.middleware import middleware
from core.openapi import openapi

import uvicorn

from routes import routes

app_config = Config.get(AppConfig)
openapi_url = f'/{app_config.app_name}' + '/openapi.json' if app_config.is_prod_or_test() else '/openapi.json'
# server_url = f'http://127.0.0.1:{app_config.port}'
app = FastAPI(
    lifespan=lifespan,
    title=app_config.app_name,
    debug=app_config.app_debug,
    responses={200: {'description': '成功'}},
    docs_url='/docs' if not app_config.is_prod() else None,
    openapi_url=openapi_url,
    # servers=[{'url': server_url}],
)
ExceptionHandler.register_exception_handler(app)
app.openapi = openapi(app.openapi)
middleware.register(app)  # 将中间件注册移到路由之前
routes.register(app)
# mcp.register(app)

mcp = FastMCP.from_fastapi(
    app=app,
    name='McpApp',
    timeout=5.0,
)
mcp.run(transport='streamable-http', host='0.0.0.0', port=8000)


if __name__ == '__main__':
    config = AppConfig()
    uvicorn.run('main:app', host=config.host, port=config.port, workers=1)
