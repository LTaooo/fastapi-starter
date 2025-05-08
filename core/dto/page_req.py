from pydantic import BaseModel, Field


class PageReq(BaseModel):
    page: int | None = Field(title='页码', examples=[1, 2], description='页码', gt=0, default=None)
    limit: int | None = Field(title='每页数量', examples=[1, 2], description='每页数量', gt=0, default=None)

    def get_offset(self) -> int | None:
        if self.page is None or self.limit is None:
            return None
        return (self.page - 1) * self.limit
