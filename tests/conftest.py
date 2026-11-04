from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from core.mysql.database.app.app_database import AppDatabase
from core.mysql.database.app.app_session import AppSession
from main import app


@pytest.fixture(scope='function')
async def database() -> AsyncGenerator[None, None]:
    if not AppDatabase.get_config().enable:
        pytest.skip('MySQL未启用')
    AppDatabase.init()
    yield
    await AppDatabase.close()


@pytest.fixture(scope='function')
async def client(database: None) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://127.0.0.1:8000') as ac:
        yield ac


@pytest.fixture(scope='function')
async def app_session(database: None) -> AsyncGenerator[AppSession, None]:
    async with AppDatabase.with_session() as session:
        yield session
