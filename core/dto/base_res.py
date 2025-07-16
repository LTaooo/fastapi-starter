from abc import ABC
from typing import Generic, Self
from pydantic import BaseModel

from core.types.types import MODEL_TYPE, SQL_MODEL_TYPE
from core.dto.page_res import PageRes
from core.mysql.page_resource import PageResource


# noinspection PyArgumentList
class BaseRes(ABC, BaseModel, Generic[MODEL_TYPE, SQL_MODEL_TYPE]):
    @classmethod
    def from_model_list(cls, data: list[SQL_MODEL_TYPE]) -> list[Self]:
        return [cls.from_model(model) for model in data]

    @classmethod
    def from_model(cls, data: SQL_MODEL_TYPE) -> Self:
        return cls(**data.__dict__)

    @classmethod
    def from_model_or_none(cls, data: SQL_MODEL_TYPE | None) -> Self | None:
        if data is None:
            return None
        return cls.from_model(data)

    @classmethod
    def from_page_resource(cls, data: PageResource[SQL_MODEL_TYPE]) -> 'PageRes[Self]':
        model_list = cls.from_model_list(data.data)
        return PageRes.from_page(model_list, data.page, data.limit, data.total)
