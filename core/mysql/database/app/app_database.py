from config.mysql_config import MysqlConfig
from core.config import Config
from core.mysql.base_mysql import BaseMysql
from typing import AsyncGenerator
from core.mysql.database.app.app_session import AppSession


class AppDatabase(BaseMysql):
    @classmethod
    def get_config(cls) -> MysqlConfig:
        return Config.get(MysqlConfig)

    @classmethod
    async def session(cls) -> AsyncGenerator[AppSession, None]:
        """
        获取一个异步MySQL会话, 不会自动commit和rollback, 如果涉及写操作, 需要手动commit
        :return:
        """
        async with cls._session() as session:
            yield AppSession(session)

    @classmethod
    async def auto_commit_session(cls) -> AsyncGenerator[AppSession, None]:
        """
        获取一个异步MySQL会话, 会自动commit和rollback
        :return:
        """
        async with cls._auto_commit_session() as session:
            yield AppSession(session)
