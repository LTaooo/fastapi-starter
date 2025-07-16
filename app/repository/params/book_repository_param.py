from pydantic import Field, BaseModel

from core.mysql.base_filter import BaseFilter
from core.util.datetime import DateTime


class BookFilter(BaseFilter):
    ids: list[int] | None = Field(default=None, description='书籍id')
    name_like: str | None = Field(default=None, description='书名')


class BookCreate(BaseModel):
    name: str = Field(description='书名')
    created_at: int = Field(description='创建时间', default_factory=DateTime.timestamp)
    updated_at: int = Field(description='更新时间', default_factory=DateTime.timestamp)
