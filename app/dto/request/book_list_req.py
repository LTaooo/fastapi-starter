from pydantic import BaseModel, Field

from core.dto.page_req import PageReq


class BookListReq(PageReq, BaseModel):
    ids: list[int] | None = Field(default=None, description='书籍id')
    name: str | None = Field(default=None, description='书名')
    pass
