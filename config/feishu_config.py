from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig


class FeishuConfig(BaseNacosConfig):
    enable: bool = Field(description='是否启用飞书告警', default=False, alias='feishu.enable')
    webhook: str = Field(description='飞书机器人Webhook地址', default='', alias='feishu.webhook')
    secret: str = Field(description='飞书机器人签名密钥', default='', alias='feishu.secret')
    timeout: int = Field(description='请求超时时间(秒)', default=5, ge=1, alias='feishu.timeout')
