from typing import TypeVar
from pydantic import BaseModel

SQL_MODEL_TYPE = TypeVar('SQL_MODEL_TYPE')

MODEL_TYPE = TypeVar('MODEL_TYPE', bound=BaseModel)
