import asyncio

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field


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
        name='common-tools-service',
    ),
    MCPConfig(
        openapi_url='https://mr-agent-test.suntekcorps.com/mr-tools-service/openapi.json',
        server_url='https://mr-agent-test.suntekcorps.com/mr-tools-service',
        name='mr-tools-service',
    ),
]

main_mcp = FastMCP(name='MainMCP')
async def init():
    """
    主mcp导入其它mcp
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


if __name__ == '__main__':
    asyncio.run(init())
    main_mcp.run(transport='streamable-http')