from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class MysqlConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    host: str = Field(description='数据库主机', alias='MYSQL_HOST')
    port: int = Field(description='数据库端口', alias='MYSQL_PORT')
    user: str = Field(description='数据库用户名', alias='MYSQL_USER')
    password: str = Field(description='数据库密码', alias='MYSQL_PASSWORD')
    database: str = Field(description='数据库名称', alias='MYSQL_DB')
    echo: bool = Field(description='是否打印SQL语句', default=False, alias='MYSQL_ECHO')
