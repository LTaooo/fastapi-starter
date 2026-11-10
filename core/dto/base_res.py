from abc import ABC
from typing import Any, Generic, TypeVar
from pydantic import BaseModel

from core.types.types import SQL_MODEL_TYPE
from core.dto.page_res import PageRes
from core.mysql.page_resource import PageResource

RESPONSE_TYPE = TypeVar('RESPONSE_TYPE', bound='BaseRes[Any]')


# noinspection PyArgumentList
class BaseRes(ABC, BaseModel, Generic[SQL_MODEL_TYPE]):
    @classmethod
    def from_model_list(cls: type[RESPONSE_TYPE], data: list[SQL_MODEL_TYPE]) -> list[RESPONSE_TYPE]:
        return [cls.from_model(model) for model in data]

    @classmethod
    def from_model(cls: type[RESPONSE_TYPE], data: SQL_MODEL_TYPE) -> RESPONSE_TYPE:
        return cls.model_validate(data, from_attributes=True)

    @classmethod
    def from_model_or_none(cls: type[RESPONSE_TYPE], data: SQL_MODEL_TYPE | None) -> RESPONSE_TYPE | None:
        if data is None:
            return None
        return cls.from_model(data)

    @classmethod
    def from_page_resource(cls: type[RESPONSE_TYPE], data: PageResource[SQL_MODEL_TYPE]) -> PageRes[RESPONSE_TYPE]:
        model_list = cls.from_model_list(data.data)
        return PageRes.from_page(model_list, data.page, data.limit, data.total)
