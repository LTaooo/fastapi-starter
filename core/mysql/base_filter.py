from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import UnaryExpression


class BaseFilter(BaseModel):
    page: int | None = Field(default=None, description='页码')
    limit: int | None = Field(default=None, description='每页数量')
    order_bys: list[UnaryExpression] = Field(default_factory=list, exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_offset(self) -> int:
        if self.page is None or self.limit is None:
            return 0
        return (self.page - 1) * self.limit

    def order_by(self, order_by: UnaryExpression):
        if self.order_bys is None:
            self.order_bys = []
        self.order_bys.append(order_by)
        return self
