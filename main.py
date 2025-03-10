from fastapi import FastAPI
from starlette.responses import JSONResponse

from app.controller import book_controller
from core.exception_handle import ExceptionHandler
from core.response import Response
from core.status_enum import StatusEnum

app = FastAPI()
app.include_router(book_controller.router)

ExceptionHandler.register_exception_handler(app)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
def default_route(path: str):
    """缺省路由"""
    return Response.error(message=f"{path} not found", code=StatusEnum.error)
