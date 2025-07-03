from fastapi import APIRouter

from core.dto.common_res import CommonRes
from app.dto.request.book_get_req import BookGetReq
from app.dto.response.book_get_res import BookGetRes
from core.mcp.operation_enums import OperationEnum
from core.response import Response

router = APIRouter(prefix='/api/book', tags=['book'])


class BookController:
    @staticmethod
    @router.post('/get', summary='根据id获取书, 返回书籍详情', operation_id=OperationEnum.get_book.value.id)
    async def get(param: BookGetReq) -> CommonRes[BookGetRes]:
        return Response.success('hello')
