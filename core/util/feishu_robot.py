import base64
import hashlib
import hmac
from datetime import datetime

import aiohttp

from config.app_config import AppConfig
from config.feishu_config import FeishuConfig
from core.config import Config
from core.logger import Logger

_MAX_CONTENT_LENGTH = 2000
_MAX_TAIL_LENGTH = 500


class FeishuRobot:
    """
    飞书机器人
    """

    @classmethod
    async def send_text_message(cls, content: str) -> None:
        try:
            config = Config.get(FeishuConfig)
            if not config.enable or not config.webhook:
                return

            app_config = Config.get(AppConfig)
            content = '\n'.join([f'项目: {app_config.app_name}', f'环境: {app_config.app_env.value}', f'错误信息: {content}'])
            if len(content) > _MAX_CONTENT_LENGTH:
                marker = '\n...(已截断)...\n'
                head_length = _MAX_CONTENT_LENGTH - _MAX_TAIL_LENGTH - len(marker)
                content = content[:head_length] + marker + content[-_MAX_TAIL_LENGTH:]

            data = {'msg_type': 'text', 'content': {'text': content}}
            if config.secret:
                timestamp = str(int(datetime.now().timestamp()))
                data['timestamp'] = timestamp
                data['sign'] = cls._gen_sign(timestamp, config.secret)

            await cls._post_request(config.webhook, data, config.timeout)
        except Exception as e:
            Logger.get().error(f'机器人发送消息失败: {e}')

    @classmethod
    async def _post_request(cls, url: str, data: dict, timeout: int) -> None:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.post(url, json=data) as response:
                response.raise_for_status()

    @classmethod
    def _gen_sign(cls, timestamp: str, secret: str) -> str:
        # 飞书签名: 以 "{timestamp}\n{secret}" 为密钥, 对空消息做 HMAC-SHA256 后 base64
        string_to_sign = f'{timestamp}\n{secret}'
        hmac_code = hmac.new(string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
        return base64.b64encode(hmac_code).decode('utf-8')
