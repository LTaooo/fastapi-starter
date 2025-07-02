from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.responses import JSONResponse
from fastapi import Request, status, FastAPI

from config.app_config import AppConfig
from core.config import Config
from core.exception.runtime_exception import RuntimeException
from core.logger import Logger
from core.response import Response
from core.status_enum import StatusEnum
from core.util.feishu_robot import FeishuRobot
from core.util.helper import Helper


def register(app: FastAPI):
    @app.exception_handler(HTTPException)
    def _http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=Response.error(message=exc.detail, code=StatusEnum.error).model_dump(),
        )

    @app.exception_handler(RuntimeException)
    def _runtime_exception_handler(request: Request, exc: RuntimeException):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=Response.error(message=exc.message, code=exc.code).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    def _validation_exception_handler(request: Request, exc: RequestValidationError):
        error_details = []
        for error in exc.errors():
            field_path = '.'.join(map(str, error['loc']))
            error_details.append({'field': field_path, 'message': error['msg']})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=Response.error(message=str(error_details), code=StatusEnum.validate_fail).model_dump(),
        )

    @app.exception_handler(Exception)
    async def _exception_handler(cls, request: Request, exc: Exception):
        # 获取堆栈信息并格式化为单一字符串
        # 获取堆栈信息并格式化为单一字符串
        message = Helper.exception_str(exc, True)
        Logger.get().error(message)
        if Config.get(AppConfig).is_prod_or_test():
            await FeishuRobot.send_text_message(message)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=Response.error(message='系统内部错误', code=StatusEnum.error).model_dump(),
        )
