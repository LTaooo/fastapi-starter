from typing import Generic
from pydantic import BaseModel

from app.types.types import SQL_MODEL_TYPE


class PageResource(BaseModel, Generic[SQL_MODEL_TYPE]):
    total: int
    data: list[SQL_MODEL_TYPE]
    limit: int
    page: int
