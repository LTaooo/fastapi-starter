from fastapi import APIRouter

from app.dto.request.book_create_req import BookCreateReq
from core.dto.common_res import CommonRes
from core.dto.page_res import PageRes
from app.dto.request.book_get_req import BookGetReq
from app.dto.request.book_list_req import BookListReq
from app.dto.response.book_get_res import BookGetRes
from app.service.book_service import BookService
from core.mcp.operation_enums import OperationEnum
from core.mysql.database.book.book_database import BookDatabase
from core.mysql.database.book.book_session import BookSession
from core.response import Response
from fastapi import Depends

router = APIRouter(prefix='/api/book', tags=['book'])


class BookController:
    @staticmethod
    @router.post('/get', summary='根据id获取书')
    async def get(param: BookGetReq, operation_id=OperationEnum.get_book.value.id) -> CommonRes[BookGetRes]:
        return Response.success('hello')
