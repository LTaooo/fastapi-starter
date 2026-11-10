from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from core.types.types import MODEL_TYPE

PAGE_MODEL_TYPE = TypeVar('PAGE_MODEL_TYPE', bound=BaseModel)


class PageRes(BaseModel, Generic[MODEL_TYPE]):
    page: int = Field(title='页码', examples=[1, 2], description='页码', gt=0)
    limit: int = Field(title='每页数量', examples=[1, 2], description='每页数量', gt=0)
    total: int = Field(title='总数量', examples=[1, 2], description='总数量', ge=0, default=0)
    data: list[MODEL_TYPE] = Field(title='数据列表')

    @classmethod
    def from_page(cls, data: list[PAGE_MODEL_TYPE], page: int, limit: int, total: int) -> 'PageRes[PAGE_MODEL_TYPE]':
        return PageRes(page=page, limit=limit, total=total, data=data)
