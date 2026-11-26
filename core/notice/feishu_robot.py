from typing import Any, ClassVar

from core.notice.feishu_api import FeishuApi, FeishuTextContent, FeishuTextReq
from config.app_config import AppConfig
from core.config import Config
from core.logger import Logger


class FeishuRobot:
    """为应用错误通知补充项目和环境信息。"""

    default_group: ClassVar[str] = '603bc7ea-d763-4363-94a4-xxxx'
    default_token: ClassVar[str] = 'xxx'

    @classmethod
    async def send_text_message(cls, content: str, group: str | None = '', token: str | None = None) -> dict[str, Any] | None:
        """发送错误通知；群组标识或签名密钥为空时使用默认值，发送失败返回 None。"""
        config = Config().get(AppConfig)
        text = '\n'.join([f'项目: {config.app_name}', f'环境: {config.app_env.value}', f'错误信息: {content}'])
        request = FeishuTextReq(content=FeishuTextContent(text=text))
        try:
            return await FeishuApi().send_text(request, group or cls.default_group, token or cls.default_token)
        except Exception as exception:
            Logger.get().error('机器人发送消息失败 reason={}', type(exception).__name__)
            return None
