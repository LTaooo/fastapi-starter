from fastapi import APIRouter

from app.dto.request.book_create_req import BookCreateReq
from core.dto.common_res import CommonRes
from core.dto.page_res import PageRes
from app.dto.request.book_get_req import BookGetReq
from app.dto.request.book_list_req import BookListReq
from app.dto.response.book_get_res import BookGetRes
from app.service.book_service import BookService
from core.mysql.database.book.book_database import BookDatabase
from core.mysql.database.book.book_session import BookSession
from core.response import Response
from fastapi import Depends

router = APIRouter(prefix='/api/book', tags=['book'])


class BookController:
    @staticmethod
    @router.post('/get', summary='根据id获取书')
    async def get(param: BookGetReq, session: BookSession = Depends(BookDatabase.session)) -> CommonRes[BookGetRes]:
        model = await BookService.get(session, param.id)
        return Response.success(BookGetRes.from_model_or_none(model))

    @staticmethod
    @router.post('/list', summary='获取书籍分页列表')
    async def list(param: BookListReq, session: BookSession = Depends(BookDatabase.session)) -> CommonRes[PageRes[BookGetRes]]:
        data = await BookService.page_list(session, param)
        result = BookGetRes.from_page_resource(data)
        return Response.success(result)

    @staticmethod
    @router.post('/create', summary='创建书籍')
    async def create(param: BookCreateReq, session: BookSession = Depends(BookDatabase.auto_commit_session)) -> CommonRes[BookGetRes]:
        model = await BookService.create(session, param)
        return Response.success(BookGetRes.from_model(model))
