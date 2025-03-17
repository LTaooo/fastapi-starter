from pydantic import BaseModel

from core.dto.page_req import PageReq


class BookListReq(PageReq, BaseModel):
    pass
