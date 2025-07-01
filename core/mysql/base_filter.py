from pydantic import BaseModel, Field


class BaseFilter(BaseModel):
    page: int | None = Field(default=None, description='页码')
    limit: int | None = Field(default=None, description='每页数量')
