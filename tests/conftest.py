from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport

from core.mysql.database.app.app_database import AppDatabase
from main import app


@pytest.fixture(scope='function')
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def db_connection():
        AppDatabase.init()
        async with AppDatabase.with_session() as session:
            yield session
        await AppDatabase.close()

    app.dependency_overrides[AppDatabase.get_session] = db_connection
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://127.0.0.1:8000') as ac:
        yield ac
    app.dependency_overrides.clear()
