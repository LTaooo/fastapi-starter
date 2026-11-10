from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig


class LogConfig(BaseNacosConfig):
    """日志输出配置。"""

    file_enable: bool = Field(description='是否输出文件日志', default=True, alias='log.file_enable')
    level: str = Field(description='日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL', default='INFO', alias='log.level')
    rotation: str = Field(description='日志轮转大小，如 50 MB、1 day', default='50 MB', alias='log.rotation')
    retention: str = Field(description='日志保留时间，如 10 days、1 month', default='10 days', alias='log.retention')
