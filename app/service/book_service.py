from app.dto.request.book_list_req import BookListReq
from app.dto.request.book_create_req import BookCreateReq
from app.model.book import Book
from app.repository.book_repository import BookRepository
from app.repository.params.book_filter import BookFilter
from core.mysql.database.app.app_session import AppSession
from core.mysql.page_resource import PageResource


class BookService:
    def __init__(self, book_repository: BookRepository):
        self.bookRepository = book_repository

    async def get(self, session: AppSession, ident: int) -> Book | None:
        return await self.bookRepository.find(session, ident)

    async def list(self, session: AppSession, req: BookListReq) -> list[Book]:
        return await self.bookRepository.list(session, self.list_req_to_filter(req))

    async def page_list(self, session: AppSession, req: BookListReq) -> PageResource[Book]:
        param = self.list_req_to_filter(req)
        param.page = param.page if param.page else 1
        param.limit = param.limit if param.limit else 20
        return await self.bookRepository.page_list(session, param)

    async def create(self, session: AppSession, req: BookCreateReq) -> Book:
        result = await self.bookRepository.create(session, req)
        return result

    def list_req_to_filter(self, req: BookListReq) -> BookFilter:
        return BookFilter(**req.model_dump())
