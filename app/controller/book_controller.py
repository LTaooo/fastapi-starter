from typing import Annotated

from fastapi import APIRouter, Body

from app.dto.request.book_req import BookGetReq, BookListReq, BookCreateReq, BookBulkUpdateNameReq
from core.di.container import Container
from core.dto.common_res import CommonRes
from core.dto.page_res import PageRes
from app.dto.response.book_res import BookGetRes
from app.service.book_service import BookService
from core.mysql.database.app.app_database import AppDatabase
from core.mysql.database.app.app_session import AppSession
from core.response import Response
from fastapi import Depends

router = APIRouter(prefix='/api/book', tags=['book'])

_book_service = Container().get(BookService)


@router.post('/get', summary='根据id获取书')
async def get_book(param: BookGetReq, session: AppSession = Depends(AppDatabase.get_session)) -> CommonRes[BookGetRes]:
    model = await _book_service.get(session, param.id)
    return Response.success(BookGetRes.from_model_or_none(model))


@router.post('/list', summary='获取书籍分页列表')
async def list_book(param: BookListReq, session: AppSession = Depends(AppDatabase.get_session)) -> CommonRes[PageRes[BookGetRes]]:
    data = await _book_service.page_list(session, param)
    result = BookGetRes.from_page_resource(data)
    return Response.success(result)


@router.post('/create', summary='创建书籍')
async def create_book(param: BookCreateReq, session: AppSession = Depends(AppDatabase.get_session)) -> CommonRes[BookGetRes]:
    model = await _book_service.create(session, param)
    return Response.success(BookGetRes.from_model(model))


@router.post('/bulk_update_name', summary='批量更新书籍名称')
async def bulk_update_name(
    books: Annotated[list[BookBulkUpdateNameReq], Body(embed=True)], session: AppSession = Depends(AppDatabase.get_session)
) -> CommonRes[None]:
    await _book_service.bulk_update_name(session, books)
    return Response.success(None)
