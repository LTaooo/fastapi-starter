from typing import Any, TypeVar, Generic

from pydantic import BaseModel, Field

from core.dto.page_req import PageReq

T = TypeVar('T')


class PageRes(BaseModel, Generic[T]):
    page: int = Field(title="页码", examples=[1, 2], description="页码", gt=0)
    limit: int = Field(title="每页数量", examples=[1, 2], description="每页数量", gt=0)
    data: list[T] = Field(title="数据")

    @classmethod
    def from_page(cls, page_req: PageReq, data: list[T]) -> "PageRes[T]":
        return PageRes(page=page_req.page, limit=page_req.limit, data=data)
