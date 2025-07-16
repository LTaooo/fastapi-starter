from typing import TypeVar
from pydantic import BaseModel

from core.mysql.base_filter import BaseFilter
from core.mysql.orm.base_sql_model import BaseSQLModel

SQL_MODEL_TYPE = TypeVar('SQL_MODEL_TYPE', bound=BaseSQLModel)

FILTER_TYPE = TypeVar('FILTER_TYPE', bound=BaseFilter)

MODEL_TYPE = TypeVar('MODEL_TYPE', bound=BaseModel)
