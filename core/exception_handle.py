from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.responses import JSONResponse
from fastapi import Request, status, FastAPI

from core.exception.runtime_exception import RuntimeException
from core.response import Response
from core.status_enum import StatusEnum


class ExceptionHandler:
    @classmethod
    def _validation_exception_handler(cls, request: Request, exc: RequestValidationError):
        # 提取错误信息
        error_details = []
        for error in exc.errors():
            field_path = ".".join(map(str, error["loc"]))
            error_details.append({
                "field": field_path,
                "message": error["msg"]
            })

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=Response.error(message=str(error_details), code=StatusEnum.validate_fail).model_dump())

    @classmethod
    def _runtime_exception_handler(cls, request: Request, exc: RuntimeException):
        return JSONResponse(status_code=status.HTTP_200_OK, content=Response.error(message=exc.message, code=exc.code).model_dump())

    @classmethod
    def _exception_handler(cls, request: Request, exc: Exception):
        return JSONResponse(status_code=status.HTTP_200_OK, content=Response.error(message="系统内部错误", code=StatusEnum.error).model_dump())
    
    @classmethod
    def _http_exception_handler(cls, request: Request, exc: HTTPException):
        return JSONResponse(status_code=status.HTTP_200_OK, content=Response.error(message=exc.detail, code=StatusEnum.error).model_dump())

    @classmethod
    def register_exception_handler(cls, app: FastAPI):
        app.add_exception_handler(RequestValidationError, ExceptionHandler._validation_exception_handler) # type: ignore
        app.add_exception_handler(RuntimeException, ExceptionHandler._runtime_exception_handler) # type: ignore
        app.add_exception_handler(HTTPException, ExceptionHandler._http_exception_handler) # type: ignore
        app.add_exception_handler(Exception, ExceptionHandler._exception_handler)
