from typing import TypeVar
from pydantic import BaseModel
from sqlmodel import SQLModel


SQL_MODEL_TYPE = TypeVar('SQL_MODEL_TYPE', bound=SQLModel)

MODEL_TYPE = TypeVar('MODEL_TYPE', bound=BaseModel)
