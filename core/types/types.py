from typing import TypeVar
from pydantic import BaseModel
from sqlmodel import SQLModel

from core.mysql.base_filter import BaseFilter

SQL_MODEL_TYPE = TypeVar('SQL_MODEL_TYPE', bound=SQLModel)

FILTER_TYPE = TypeVar('FILTER_TYPE', bound=BaseFilter)

MODEL_TYPE = TypeVar('MODEL_TYPE', bound=BaseModel)
