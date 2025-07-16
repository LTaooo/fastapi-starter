from sqlalchemy.ext.asyncio import AsyncSession

from core.mysql.base_mysql_session import BaseMysqlSession


class AppSession(BaseMysqlSession):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
