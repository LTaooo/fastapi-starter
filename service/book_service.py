from dto.request.book_list_req import BookListReq
from model.book import Book
from repository.book_repository import BookRepository


class BookService:
    @classmethod
    async def get(cls, ident: int) -> Book | None:
        return await BookRepository.find(ident)

    @classmethod
    async def list(cls, req: BookListReq) -> list[Book]:
        return await BookRepository.list(req)