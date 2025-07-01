from pydantic import BaseModel, Field

from core.dto.page_req import PageReq


class BookCreateReq(BaseModel):
    name: str = Field(description='书名')


class BookGetReq(BaseModel):
    id: int = Field(examples=[1, 2], description='书籍id', gt=0)


class BookListReq(PageReq, BaseModel):
    ids: list[int] | None = Field(default=None, description='书籍id')
    name: str | None = Field(default=None, description='书名')
    pass
