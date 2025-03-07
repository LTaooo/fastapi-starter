from sqlmodel import SQLModel, Field

class Book(SQLModel, table=True):
    __tablename__ = 'book'

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False, description='书名')
    created_at: int = Field(nullable=False, description='创建时间')
    updated_at: int = Field(nullable=False, description='修改时间')