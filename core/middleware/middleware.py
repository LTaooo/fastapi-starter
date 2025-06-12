import uuid

from fastapi import FastAPI
from starlette.requests import Request

from core.context import Context


def register(app: FastAPI):
    @app.middleware('http')
    async def add_request_id_middleware(request: Request, call_next):
        req_id = str(uuid.uuid4())
        request.state.request_id = req_id
        Context.set_request_id(req_id)
        response = await call_next(request)
        response.headers['X-Request-ID'] = req_id
        return response
