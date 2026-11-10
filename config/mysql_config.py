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
    pool_size: int = Field(description='连接池大小', default=5, gt=0, alias='mysql.pool_size')
    max_overflow: int = Field(description='连接池最大溢出连接数', default=50, ge=0, alias='mysql.max_overflow')
    pool_timeout: float = Field(description='获取连接的超时时间（秒）', default=30, gt=0, alias='mysql.pool_timeout')
    pool_recycle: int = Field(description='连接回收时间（秒），-1 表示不回收', default=3600, ge=-1, alias='mysql.pool_recycle')
    pool_pre_ping: bool = Field(description='使用连接前是否检查可用性', default=True, alias='mysql.pool_pre_ping')
