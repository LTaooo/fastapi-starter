from pydantic import BaseModel
from sqlmodel import SQLModel
from typing import Generic, TypeVar

T = TypeVar('T', bound=SQLModel)


class PageResource(BaseModel, Generic[T]):
    total: int
    data: list[T]
    limit: int
    page: int
