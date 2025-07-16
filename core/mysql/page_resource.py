from typing import Generic
from pydantic import BaseModel, ConfigDict

from core.types.types import SQL_MODEL_TYPE


class PageResource(BaseModel, Generic[SQL_MODEL_TYPE]):
    total: int
    data: list[SQL_MODEL_TYPE]
    limit: int
    page: int
    model_config = ConfigDict(arbitrary_types_allowed=True)
