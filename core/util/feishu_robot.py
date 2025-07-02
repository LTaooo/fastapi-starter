import base64
import hashlib
import hmac
from datetime import datetime
from typing import ClassVar

import aiohttp
import json
from loguru import logger

from config.app_config import AppConfig
from core.config import Config


class FeishuRobot:
    """
    飞书机器人
    """

    base_url: ClassVar[str] = 'https://open.feishu.cn/open-apis/bot/v2/hook/'

    default_group: ClassVar[str] = '603bc7ea-d763-4363-94a4-xxxx'
    default_token: ClassVar[str] = 'xxx'

    @classmethod
    async def send_text_message(cls, content: str, group: str | None = '', token: str | None = None):
        """
        发送文本消息到飞书群
        :param content: 要发送的文本内容
        :param group: 群组ID, 默认为default_group
        :param token: token, 默认为default_token
        :return: 响应结果
        """
        url = cls.base_url + (group or cls.default_group)
        token = token or cls.default_token
        timestamp = str(int(datetime.now().timestamp()))
        sign = cls._gen_sign(timestamp, token)
        content = '\n'.join(
            [f'项目: {Config().get(AppConfig).app_name}', f'环境: {Config().get(AppConfig).app_env.value}', f'错误信息: {content}']
        )
        data = {'msg_type': 'text', 'content': {'text': content}, 'timestamp': timestamp, 'sign': sign}
        try:
            result = await cls._post_request(url, data)
            return result
        except Exception as e:
            logger.error(f'机器人发送消息时出现请求错误: {e}')
        return None

    @classmethod
    async def _post_request(cls, url, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data)) as response:
                response.raise_for_status()  # 检查响应状态码
                return await response.json()

    @classmethod
    def _gen_sign(cls, timestamp: str, secret):
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
