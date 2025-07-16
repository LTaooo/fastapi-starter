from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.mysql.orm.auto_time import AutoTime
from core.mysql.orm.base_sql_model import BaseSQLModel


class Book(BaseSQLModel, AutoTime):
    __tablename__ = 'book'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment='书名')
    created_at: Mapped[int] = mapped_column(Integer, nullable=False, comment='创建时间')
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False, comment='修改时间')
