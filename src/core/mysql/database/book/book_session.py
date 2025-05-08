from core.mysql.base_mysql_session import BaseMysqlSession
from sqlmodel.ext.asyncio.session import AsyncSession


class BookSession(BaseMysqlSession):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
