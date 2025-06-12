from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig


class MysqlConfig(BaseNacosConfig):
    host: str = Field(description='数据库主机', alias='mysql.host')
    port: int = Field(description='数据库端口', alias='mysql.port')
    user: str = Field(description='数据库用户名', alias='mysql.user')
    password: str = Field(description='数据库密码', alias='mysql.password')
    database: str = Field(description='数据库名称', alias='mysql.db')
    echo: bool = Field(description='是否打印SQL语句', default=False, alias='mysql.echo')
