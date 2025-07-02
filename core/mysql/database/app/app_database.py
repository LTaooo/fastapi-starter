from config.mysql_config import MysqlConfig
from core.config import Config
from core.mysql.base_mysql import BaseMysql
from typing import Type
from core.mysql.database.app.app_session import AppSession


class AppDatabase(BaseMysql[AppSession]):
    @classmethod
    def get_config(cls) -> MysqlConfig:
        return Config.get(MysqlConfig)

    @classmethod
    def session_class(cls) -> Type[AppSession]:
        return AppSession
