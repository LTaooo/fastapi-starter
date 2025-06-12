from pydantic import BaseModel, Field


class BookGetReq(BaseModel):
    id: int = Field(examples=[1, 2], description='书籍id', gt=0)
