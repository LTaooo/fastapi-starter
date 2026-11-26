import base64
import hashlib
import hmac
import json
from datetime import datetime
from http import HTTPMethod
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from core.http.base_api import BaseApi
from core.http.api_exception import ApiResponseError


class FeishuTextContent(BaseModel):
    """飞书文本消息的内容。"""

    text: str


class FeishuTextReq(BaseModel):
    """不含签名的飞书文本消息请求。"""

    msg_type: Literal['text'] = 'text'
    content: FeishuTextContent


class FeishuRes(BaseModel):
    """飞书机器人响应；保留未声明的协议字段。"""

    model_config = ConfigDict(extra='allow')

    code: int | None = None
    msg: str | None = None


class FeishuApi(BaseApi):
    """飞书自定义机器人的 Webhook 客户端。"""

    base_url: ClassVar[str] = 'https://open.feishu.cn/open-apis/bot/v2/hook/'
    # 全局异常处理器在返回错误响应前会同步等待通知，超时必须留在秒级，否则上游网络黑洞会拖住响应
    _timeout_seconds: ClassVar[float] = 10

    async def send_text(self, request: FeishuTextReq, group: str, token: str | None = None) -> dict[str, Any]:
        """按 Webhook 标识发送文本；传入签名密钥时附加时间戳与签名，返回原始响应字典。"""
        payload = request.model_dump(mode='json')
        if token:
            timestamp = str(int(datetime.now().timestamp()))
            payload.update(timestamp=timestamp, sign=self._generate_signature(timestamp, token))

        response = await self.request_json(
            HTTPMethod.POST,
            self.base_url + group,
            timeout_seconds=self._timeout_seconds,
            raw_body=json.dumps(payload),
            retry_times=0,
        )

        try:
            FeishuRes.model_validate(response)
        except ValidationError:
            raise ApiResponseError('飞书机器人响应格式无效') from None
        return response

    @staticmethod
    def _generate_signature(timestamp: str, secret: str) -> str:
        """将 Unix 秒字符串与密钥用换行拼接，作为 HMAC-SHA256 密钥对空消息签名。"""
        signing_key = f'{timestamp}\n{secret}'.encode('utf-8')
        digest = hmac.new(signing_key, digestmod=hashlib.sha256).digest()
        return base64.b64encode(digest).decode('utf-8')
