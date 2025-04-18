from app.dto.request.book_list_req import BookListReq
from app.dto.request.book_create_req import BookCreateReq
from app.model.book import Book
from app.repository.book_repository import BookRepository
from core.mysql.page_resource import PageResource
from sqlmodel.ext.asyncio.session import AsyncSession


class BookService:
    @classmethod
    async def get(cls, session: AsyncSession, ident: int) -> Book | None:
        return await BookRepository.find(session, ident)

    @classmethod
    async def list(cls, session: AsyncSession, req: BookListReq) -> list[Book]:
        return await BookRepository.list(session, req)

    @classmethod
    async def page_list(cls, session: AsyncSession, req: BookListReq) -> PageResource[Book]:
        return await BookRepository.page_list(session, req)

    @classmethod
    async def create(cls, session: AsyncSession, req: BookCreateReq) -> Book:
        result = await BookRepository.create(session, req)
        return result
