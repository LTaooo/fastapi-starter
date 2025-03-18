import pytest
from httpx import AsyncClient, ASGITransport

from core.mysql.mysql import Mysql
from main import app


@pytest.fixture(scope='function')
async def client():
    """提供一个在整个测试会话中共享的 HTTP 客户端"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://127.0.0.1:8000') as ac:
        yield ac
    await Mysql().close()
