from abc import ABC
from typing import TypeVar
from pydantic import BaseModel

from core.dto.page_req import PageReq
from core.dto.page_res import PageRes

T = TypeVar('T', bound=BaseModel)


class BaseRes(ABC, BaseModel):

    # noinspection PyArgumentList
    @classmethod
    def from_model_list(cls, data: list[T]) -> list["BaseRes"]:
        # 使用 cls 来实例化具体的子类对象
        return [cls(**model.model_dump()) for model in data]

    # noinspection PyArgumentList
    @classmethod
    def from_model(cls, data: T | None) -> list["BaseRes"] | None:
        return None if data is None else cls(**data.model_dump())

    @classmethod
    def model_to_page(cls, page: PageReq, data: list[T]) -> "PageRes[T]":
        return PageRes.from_page(page, cls.from_model_list(data))