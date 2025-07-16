from sqlmodel import Field

from core.mysql.orm.auto_time import AutoTime
from core.mysql.orm.base_sql_model import BaseSQLModel


class Book(BaseSQLModel, AutoTime, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False, description='书名')
    created_at: int = Field(nullable=False, description='创建时间')
    updated_at: int = Field(nullable=False, description='修改时间')
