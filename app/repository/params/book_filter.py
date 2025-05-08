from pydantic import BaseModel, Field


class BookFilter(BaseModel):
    ids: list[int] | None = Field(default=None, description='书籍id')
    name: str | None = Field(default=None, description='书名')
    page: int | None = Field(default=None, description='页码')
    limit: int | None = Field(default=None, description='每页数量')
