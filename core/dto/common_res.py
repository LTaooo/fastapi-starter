from typing import TypeVar, Generic, Optional, Union, List
from pydantic import BaseModel, Field
from core.status_enum import StatusEnum

T = TypeVar('T')

class CommonRes(BaseModel, Generic[T]):
    code: int = StatusEnum.success.value
    data: Optional[Union[T, List[T]]]
    message: str = Field(default="success")
