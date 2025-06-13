import asyncio
import contextvars
import json

import httpx
from fastmcp import FastMCP as FastMCPBase
from mcp import Tool
from pydantic import BaseModel, Field
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

request_params = contextvars.ContextVar('request_path', default='')


class FastMCP(FastMCPBase):
    async def _mcp_list_tools(self) -> list[Tool]:
        """
        List all available tools, in the format expected by the low-level MCP
        server.

        """
        param = request_params.get()
        server: str = ''
        if param:
            param = json.loads(param)
            server = param.get('server', '')

        # 将server参数按逗号分隔成多个值
        server_prefixes = [prefix.strip() for prefix in server.split(',')] if server else ['']

        tools = await self.get_tools()
        # 检查工具名称是否以任一server前缀开头
        return [tool.to_mcp_tool(name=key) for key, tool in tools.items() if any(key.startswith(prefix) for prefix in server_prefixes)]


class MCPConfig(BaseModel):
    openapi_url: str = Field(description='服务的openapi地址')
    server_url: str = Field(description='服务的服务器地址')
    name: str = Field(description='服务的名称')


"""
mcp服务列表
"""
mcp_services = [
    MCPConfig(
        openapi_url='https://mr-agent-test.suntekcorps.com/common-tools-service/openapi.json',
        server_url='https://mr-agent-test.suntekcorps.com/common-tools-service',
        name='common_tool',
    ),
    MCPConfig(
        openapi_url='https://mr-agent-test.suntekcorps.com/mr-tools-service/openapi.json',
        server_url='https://mr-agent-test.suntekcorps.com/mr-tools-service',
        name='mr_tool',
    ),
]

main_mcp = FastMCP(name='MainMCP')


async def init():
    """
    主mcp导入其它mcps
    """
    for mcp_service in mcp_services:
        await main_mcp.import_server(
            mcp_service.name,
            FastMCP.from_openapi(
                openapi_spec=httpx.get(mcp_service.openapi_url).json(),
                client=httpx.AsyncClient(base_url=mcp_service.server_url, timeout=60),
                name=mcp_service.name,
            ),
        )


class SimpleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_params.set(json.dumps(dict(request.query_params)))
        response = await call_next(request)
        return response


custom_middleware = [
    Middleware(SimpleMiddleware),
]


if __name__ == '__main__':
    asyncio.run(init())
    main_mcp.run(transport='streamable-http', port=8001, host='0.0.0.0', middleware=custom_middleware)
