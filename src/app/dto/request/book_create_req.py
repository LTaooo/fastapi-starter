from pydantic import BaseModel, Field


class BookCreateReq(BaseModel):
    name: str = Field(description='书名')
