from fastapi import FastAPI
from app.controller import book_controller
from core.context import Context
from core.exception_handle import ExceptionHandler
from core.lifespan import lifespan
from core.response import Response
from core.status_enum import StatusEnum


app = FastAPI(lifespan=lifespan)
Context.init(app)
app.include_router(book_controller.router)

ExceptionHandler.register_exception_handler(app)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"], include_in_schema=False)
def default_route(path: str):
    """缺省路由"""
    return Response.error(message=f"{path} not found", code=StatusEnum.error)
