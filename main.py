from dotenv import load_dotenv
from fastapi import FastAPI
from app.controller import book_controller
from config.app_config import AppConfig
from core.config import Config
from core.context import Context
from core.exception.handle.exception_handle import ExceptionHandler
from core.lifespan import lifespan
from core.openapi import openapi
from core.response import Response
from core.status_enum import StatusEnum

load_dotenv()
app_config = Config.get(AppConfig)
app = FastAPI(
    lifespan=lifespan,
    title=app_config.app_name,
    debug=app_config.app_debug,
    responses={200: {'description': '请求参数错误'}},
)
app.openapi = openapi(app.openapi)
Context.init(app)
app.include_router(book_controller.router)

ExceptionHandler.register_exception_handler(app)


@app.api_route(
    '/{path:path}',
    methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
    include_in_schema=False,
)
def default_route(path: str):
    """缺省路由"""
    return Response.error(message=f'{path} not found', code=StatusEnum.error)
