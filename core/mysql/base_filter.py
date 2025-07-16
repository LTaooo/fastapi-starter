from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import InstrumentedAttribute


class OrderBy(BaseModel):
    field: InstrumentedAttribute
    is_asc: bool
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseFilter(BaseModel):
    page: int | None = Field(default=None, description='页码')
    limit: int | None = Field(default=None, description='每页数量')
    order_bys: list[OrderBy] | None = Field(default=None, description='排序字段')

    def get_offset(self) -> int:
        if self.page is None or self.limit is None:
            return 0
        return (self.page - 1) * self.limit

    def order_by(self, field: InstrumentedAttribute, is_asc: bool = True):
        if self.order_bys is None:
            self.order_bys = []
        self.order_bys.append(OrderBy(field=field, is_asc=is_asc))
        return self
