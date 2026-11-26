import json
from http import HTTPMethod
from unittest.mock import AsyncMock, patch

from core.notice.feishu_api import FeishuApi, FeishuTextContent, FeishuTextReq


async def test_send_signed_text_preserves_webhook_protocol() -> None:
    """检查文本请求的原始 JSON、签名及原响应字段。"""
    response = {'code': 0, 'msg': 'success', 'StatusCode': 0, 'extra': {'accepted': True}}
    request = FeishuTextReq(content=FeishuTextContent(text='测试'))
    with (
        patch('core.notice.feishu_api.datetime') as clock,
        patch.object(FeishuApi, 'request_json', new_callable=AsyncMock, return_value=response) as request_json,
    ):
        clock.now.return_value.timestamp.return_value = 1700000000.25
        result = await FeishuApi().send_text(request, 'test-hook', 'test-secret')

    request_json.assert_awaited_once_with(
        HTTPMethod.POST,
        'https://open.feishu.cn/open-apis/bot/v2/hook/test-hook',
        timeout_seconds=10,
        raw_body=json.dumps(
            {
                'msg_type': 'text',
                'content': {'text': '测试'},
                'timestamp': '1700000000',
                'sign': 'mbm4Y4oluIPQ00qlBIhX8vAZ0EKv3nw0LuTb91jPL84=',
            }
        ),
        retry_times=0,
    )
    assert result is response


async def test_send_unsigned_text_preserves_nonzero_response() -> None:
    """无签名密钥时省略签名字段，HTTP 成功的业务响应仍原样返回。"""
    response = {'code': 19001, 'msg': 'rejected'}
    request = FeishuTextReq(content=FeishuTextContent(text='notice'))
    with patch.object(FeishuApi, 'request_json', new_callable=AsyncMock, return_value=response) as request_json:
        result = await FeishuApi().send_text(request, 'test-hook')

    request_json.assert_awaited_once_with(
        HTTPMethod.POST,
        'https://open.feishu.cn/open-apis/bot/v2/hook/test-hook',
        timeout_seconds=10,
        raw_body=json.dumps({'msg_type': 'text', 'content': {'text': 'notice'}}),
        retry_times=0,
    )
    assert result is response
