from fastapi import FastAPI

from app.controller.book_controller import router as book_router
from core.response import Response
from core.status_enum import StatusEnum

router = [book_router]


def register(app: FastAPI):
    for r in router:
        app.include_router(r)

    # @app.api_route(
    #     '/{path:path}',
    #     methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
    #     include_in_schema=False,
    # )
    # def default_route(path: str):
    #     """缺省路由"""
    #     return Response.error(message=f'{path} not found', code=StatusEnum.error)
