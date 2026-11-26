from typing import Annotated

from fastapi import APIRouter, Body

from app.dto.request.book_req import BookListReq, BookCreateReq, BookBulkUpdateNameReq
from core.di.dependency import inject
from core.dto.common_res import CommonRes
from core.dto.page_res import PageRes
from app.dto.response.book_res import BookGetRes
from app.service.book_service import BookService
from core.mysql.database.app.app_session_dep import SessionDep
from core.response import Response

router = APIRouter(prefix='/api/book', tags=['book'])


@router.get('/get', summary='根据id获取书')
async def get_book(book_id: int, session: SessionDep, book_service: BookService = inject(BookService)) -> CommonRes[BookGetRes]:
    """通过注入的书籍服务查询指定书籍。"""
    model = await book_service.get(session, book_id)
    return Response.success(BookGetRes.from_model_or_none(model))


@router.post('/list', summary='获取书籍分页列表')
async def list_book(param: BookListReq, session: SessionDep, book_service: BookService = inject(BookService)) -> CommonRes[PageRes[BookGetRes]]:
    """通过注入的书籍服务按条件分页查询。"""
    data = await book_service.page_list(session, param)
    result = BookGetRes.from_page_resource(data)
    return Response.success(result)


@router.post('/create', summary='创建书籍')
async def create_book(param: BookCreateReq, session: SessionDep, book_service: BookService = inject(BookService)) -> CommonRes[BookGetRes]:
    """通过注入的书籍服务创建书籍。"""
    model = await book_service.create(session, param)
    return Response.success(BookGetRes.from_model(model))


@router.post('/bulk_update_name', summary='批量更新书籍名称')
async def bulk_update_name(
    books: Annotated[list[BookBulkUpdateNameReq], Body(embed=True)],
    session: SessionDep,
    book_service: BookService = inject(BookService),
) -> CommonRes[None]:
    """通过注入的书籍服务批量更新名称。"""
    await book_service.bulk_update_name(session, books)
    return Response.success(None)
