from pydantic import BaseModel, Field

from core.dto.page_req import PageReq


class BookListReq(PageReq, BaseModel):
    pass