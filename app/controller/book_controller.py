from fastapi import APIRouter

from core.dto.common_res import CommonRes
from core.dto.page_res import PageRes
from app.dto.request.book_get_req import BookGetReq
from app.dto.request.book_list_req import BookListReq
from app.dto.response.book_get_res import BookGetRes
from app.service.book_service import BookService
from core.response import Response

router = APIRouter()


@router.post("/book/get", response_model=CommonRes[BookGetRes], summary="根据id获取书")
async def get(param: BookGetReq):
    model = await BookService.get(param.id)
    return Response.success(BookGetRes.from_model(model) if model else None)


@router.post("/book/list", response_model=CommonRes[PageRes[BookGetRes]], summary="获取书籍分页列表")
async def list_book(param: BookListReq):
    data = await BookService.page_list(param)
    result = BookGetRes.from_page_resource(data)
    return Response.success(result)
