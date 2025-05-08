from app.dto.request.book_list_req import BookListReq
from app.dto.request.book_create_req import BookCreateReq
from app.model.book import Book
from app.repository.book_repository import BookRepository
from app.repository.params.book_filter import BookFilter
from core.mysql.database.book.book_session import BookSession
from core.mysql.page_resource import PageResource


class BookService:
    @classmethod
    async def get(cls, session: BookSession, ident: int) -> Book | None:
        return await BookRepository.find(session, ident)

    @classmethod
    async def list(cls, session: BookSession, req: BookListReq) -> list[Book]:
        return await BookRepository.list(session, cls.list_req_to_filter(req))

    @classmethod
    async def page_list(cls, session: BookSession, req: BookListReq) -> PageResource[Book]:
        param = cls.list_req_to_filter(req)
        param.page = param.page if param.page else 1
        param.limit = param.limit if param.limit else 20
        return await BookRepository.page_list(session, param)

    @classmethod
    async def create(cls, session: BookSession, req: BookCreateReq) -> Book:
        result = await BookRepository.create(session, req)
        return result

    @classmethod
    def list_req_to_filter(cls, req: BookListReq) -> BookFilter:
        return BookFilter(**req.model_dump())
