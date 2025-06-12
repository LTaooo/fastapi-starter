from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport

from core.mysql.database.book.book_database import BookDatabase
from main import app


@pytest.fixture(scope='function')
async def client() -> AsyncGenerator[AsyncClient, None]:
    """提供一个在整个测试会话中共享的 HTTP 客户端"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://127.0.0.1:8000') as ac:
        BookDatabase.init()
        yield ac
        await BookDatabase.close()
