from abc import ABC
from typing import Generic, TypeVar
from pydantic import BaseModel

from core.dto.page_res import PageRes
from core.mysql.page_resource import PageResource

T = TypeVar('T', bound=BaseModel)


class BaseRes(ABC, BaseModel, Generic[T]):

    # noinspection PyArgumentList
    @classmethod
    def from_model_list(cls, data: list[T]) -> list["BaseRes|None"]:
        # 使用 cls 来实例化具体的子类对象
        return [cls.from_model(model) for model in data]

    # noinspection PyArgumentList
    @classmethod
    def from_model(cls, data: T) -> "BaseRes":
        return cls(**data.model_dump())       
    
    
    @classmethod
    def from_page_resource(cls, data: PageResource) -> "PageRes[T]":
        return PageRes.from_page(cls.from_model_list(data.data), data.page, data.limit, data.total)
