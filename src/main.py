# ruff: noqa: E402
from dotenv import load_dotenv

load_dotenv()
from core.logger import Logger
from routes import routes
from fastapi import FastAPI
from config.app_config import AppConfig
from core.config import Config
from core.exception.handle.exception_handle import ExceptionHandler
from core.lifespan import lifespan
from core.openapi import openapi
import uvicorn

app_config = Config.get(AppConfig)
app = FastAPI(
    lifespan=lifespan,
    title=app_config.app_name,
    debug=app_config.app_debug,
    responses={200: {'description': '成功'}},
    docs_url='/docs' if not app_config.is_prod() else None,
    openapi_url='/openapi.json' if not app_config.is_prod() else None,
)
ExceptionHandler.register_exception_handler(app)
app.openapi = openapi(app.openapi)
routes.register(app)

if __name__ == '__main__':
    Logger.get().info('项目启动中...')
    uvicorn.run('main:app', host='0.0.0.0', port=8000, workers=2)
