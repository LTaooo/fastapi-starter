from fastapi import APIRouter

from core.dto.common_res import CommonRes
from core.dto.page_res import PageRes
from dto.request.book_get_req import BookGetReq
from dto.request.book_list_req import BookListReq
from dto.response.book_get_res import BookGetRes
from service.book_service import BookService
from core.response import Response

router = APIRouter()


@router.post("/book/get", response_model=CommonRes[BookGetRes], summary="根据id获取书")
async def get(param: BookGetReq):
    model = await BookService.get(param.id)
    return Response.success(BookGetRes.from_model(model))


@router.post("/book/list", response_model=CommonRes[PageRes[BookGetRes]], summary="获取书籍分页列表")
async def list_book(param: BookListReq):
    data = await BookService.list(param)
    # result = PageRes.from_page(param, BookGetRes.from_model_list(data))
    result = BookGetRes.model_to_page(param, data)
    return Response.success(result)
