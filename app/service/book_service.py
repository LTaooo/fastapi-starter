from app.dto.request.book_list_req import BookListReq
from app.model.book import Book
from app.repository.book_repository import BookRepository
from core.mysql.page_resource import PageResource


class BookService:
    @classmethod
    async def get(cls, ident: int) -> Book | None:
        return await BookRepository.find(ident)

    @classmethod
    async def list(cls, req: BookListReq) -> list[Book]:
        return await BookRepository.list(req)

    @classmethod
    async def page_list(cls, req: BookListReq) -> PageResource[Book]:
        return await BookRepository.page_list(req)
