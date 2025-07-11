from enum import Enum

from pydantic import BaseModel, Field

from config.app_config import AppConfig
from core.config import Config


class Op(BaseModel):
    id: str = Field(description='tool名称, 英文,下划线分隔')
    mcp: bool = Field(default=True, description='是否需要注册到MCP')

    def __str__(self):
        return self.id


class OperationEnum(Enum):
    """
    操作枚举
    """

    # Book
    get_book = Op(id='get_book', mcp=False)
    get_book_list = Op(id='get_book_list', mcp=False)
    create_book = Op(id='create_book', mcp=Config.get(AppConfig).is_dev())

    @classmethod
    def get_mcp_operations(cls) -> list[str]:
        """
        获取所有枚举值
        """
        return [op.value.id for op in OperationEnum if op.value.mcp]
