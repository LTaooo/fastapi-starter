from abc import ABC
from sqlmodel.ext.asyncio.session import AsyncSession


class BaseMysqlSession(ABC):
    def __init__(self, session: AsyncSession):
        self._session = session

    def get_session(self):
        return self._session
