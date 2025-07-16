from config.mcp_config import MCPConfig
from core import logger
from core.dto.common_res import CommonRes
from core.exception.handle import exception_handle
from core.logger import Logger
from core.middleware import middleware
from routes import routes
from fastapi import FastAPI
from config.app_config import AppConfig
from core.config import Config
from core.lifespan import lifespan
from core.openapi import openapi
import uvicorn

app_config = Config.get(AppConfig)
logger.init()
app = FastAPI(
    lifespan=lifespan,
    title=app_config.app_name,
    debug=app_config.app_debug,
    responses={200: CommonRes(data=None).model_dump()},
    docs_url='/docs' if not app_config.is_prod() else None,
    openapi_url='/openapi.json' if not app_config.is_prod() else None,
    root_path=app_config.app_root_path,
)
exception_handle.register(app)
app.openapi = openapi(app.openapi)
routes.register(app)
middleware.register(app)

if __name__ == '__main__':
    Logger.get().info('项目启动中...')
    config = Config.get(AppConfig)
    mcp_config = Config.get(MCPConfig)
    uvicorn.run('main:app', host=config.host, port=config.port, workers=1 if mcp_config.enable else config.workers)
