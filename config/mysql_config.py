from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig


class MysqlConfig(BaseNacosConfig):
    enable: bool = Field(description='是否启用MySQL', default=True, alias='mysql.enable')
    host: str = Field(description='数据库主机', default='127.0.0.1', alias='mysql.host')
    port: int = Field(description='数据库端口', default=3306, alias='mysql.port')
    user: str = Field(description='数据库用户名', default='root', alias='mysql.user')
    password: str = Field(description='数据库密码', default='', alias='mysql.password')
    database: str = Field(description='数据库名称', default='', alias='mysql.db')
    echo: bool = Field(description='是否打印SQL语句', default=False, alias='mysql.echo')
