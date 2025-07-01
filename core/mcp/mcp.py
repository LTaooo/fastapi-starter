from fastapi import FastAPI
from fastapi.routing import APIRoute
from mcp.server import FastMCP

from config.app_config import AppConfig
from config.mcp_config import MCPConfig
from core.config import Config
from core.logger import Logger
from core.mcp.operation_enums import OperationEnum

__register_tools = []

mcp = FastMCP(name=Config.get(AppConfig).app_name)


def register(app: FastAPI):
    config = Config.get(MCPConfig)
    app.mount(config.mount, mcp.streamable_http_app())
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.operation_id in OperationEnum.get_mcp_operations():
            if route.operation_id not in __register_tools:
                mcp.add_tool(route.endpoint, route.operation_id, route.description)
                __register_tools.append(route.operation_id)
    Logger.get().info(f'已注册mcp工具: {len(__register_tools)}')
