from pydantic import BaseModel, Field

from core.dto.base_res import BaseRes


class BookGetRes(BaseRes):
    id: int = Field(description="书籍的唯一标识符")
    name: str = Field(description="书籍的名称")
    created_at: int = Field(description="书籍的创建时间，以时间戳形式表示")
    updated_at: int = Field(description="书籍的更新时间，以时间戳形式表示")