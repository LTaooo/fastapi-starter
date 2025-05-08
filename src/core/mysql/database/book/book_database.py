from config.mysql_config import MysqlConfig
from core.config import Config
from core.mysql.base_mysql import BaseMysql
from typing import AsyncGenerator
from core.mysql.database.book.book_session import BookSession


class BookDatabase(BaseMysql):
    def get_config(self) -> MysqlConfig:
        return Config.get(MysqlConfig)

    async def session(self) -> AsyncGenerator[BookSession, None]:
        """
        获取一个异步MySQL会话, 不会自动commit和rollback, 如果涉及写操作, 需要手动commit
        :return:
        """
        async with self._session() as session:
            yield BookSession(session)

    async def auto_commit_session(self) -> AsyncGenerator[BookSession, None]:
        """
        获取一个异步MySQL会话, 会自动commit和rollback
        :return:
        """
        async with self._auto_commit_session() as session:
            yield BookSession(session)
