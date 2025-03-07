from typing import TypeVar, Generic, Optional, Union, List
from pydantic import BaseModel, Field
from starlette import status

T = TypeVar('T')

class CommonRes(BaseModel, Generic[T]):
    code: int = status.HTTP_200_OK
    data: Optional[Union[T, List[T]]]
    message: str = Field(default="success")
