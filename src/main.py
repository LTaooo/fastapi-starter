# ruff: noqa: E402
from dotenv import load_dotenv
from core.logger import Logger
from routes import routes

load_dotenv()
from fastapi import FastAPI
from config.app_config import AppConfig
from core.config import Config
from core.context import Context
from core.exception.handle.exception_handle import ExceptionHandler
from core.lifespan import lifespan
from core.openapi import openapi
import uvicorn

app_config = Config.get(AppConfig)
app = FastAPI(
    lifespan=lifespan,
    title=app_config.app_name,
    debug=app_config.app_debug,
    responses={200: {'description': '请求参数错误'}},
)
ExceptionHandler.register_exception_handler(app)
app.openapi = openapi(app.openapi)
Context.init(app)
routes.register(app)

if __name__ == '__main__':
    Logger.get().info('项目启动中...')
    uvicorn.run('main:app', host='0.0.0.0', port=8000, workers=2)
