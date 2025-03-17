from pydantic import BaseModel, Field


class PageReq(BaseModel):
    page: int = Field(title='页码', examples=[1, 2], description='页码', gt=0)
    limit: int = Field(title='每页数量', examples=[1, 2], description='每页数量', gt=0)

    def get_offset(self):
        return (self.page - 1) * self.limit
