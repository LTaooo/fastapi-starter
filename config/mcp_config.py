from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig


class MCPConfig(BaseNacosConfig):
    enable: bool = Field(description='是否开启', alias='mcp.enable', default=False)
    mount: str = Field(description='挂载路径', alias='mcp.mount', default='/')
