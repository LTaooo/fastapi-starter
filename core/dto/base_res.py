from abc import ABC
from typing import Generic, TypeVar, Self
from pydantic import BaseModel

from core.dto.page_res import PageRes
from core.mysql.page_resource import PageResource

T = TypeVar('T', bound=BaseModel)


# noinspection PyArgumentList
class BaseRes(ABC, BaseModel, Generic[T]):
    @classmethod
    def from_model_list(cls, data: list[T]) -> list['Self']:
        return [cls.from_model(model) for model in data]

    @classmethod
    def from_model(cls, data: T) -> 'Self':
        return cls(**data.model_dump())

    @classmethod
    def from_model_or_none(cls, data: T | None) -> 'Self | None':
        if data is None:
            return None
        return cls.from_model(data)

    @classmethod
    def from_page_resource(cls, data: PageResource) -> 'PageRes[Self]':
        return PageRes.from_page(cls.from_model_list(data.data), data.page, data.limit, data.total)
