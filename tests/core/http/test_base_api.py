from contextlib import asynccontextmanager
from http import HTTPMethod
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.http import base_api
from core.http.base_api import BaseApi
from core.http.api_exception import ApiResponseError, ApiTransportError


@pytest.fixture
def transport(monkeypatch):
    """模拟 aiohttp 会话和响应流，不连接真实外部接口。"""
    responses = []
    requests = []

    @asynccontextmanager
    async def request(method, url, **options):
        """按队列提供响应，记录请求参数。"""
        requests.append((method, url, options))
        status, body = responses.pop(0)

        async def chunks(size):
            """提供小响应体，模拟分块读取。"""
            yield body

        yield SimpleNamespace(status=status, content_length=len(body), content=SimpleNamespace(iter_chunked=chunks))

    @asynccontextmanager
    async def session(**options):
        """替换网络会话，只提供请求能力。"""
        yield SimpleNamespace(request=request)

    monkeypatch.setattr(base_api.aiohttp, 'ClientSession', session)
    monkeypatch.setattr(base_api.asyncio, 'sleep', AsyncMock())
    return responses, requests


@pytest.mark.parametrize(('method', 'retry_post', 'expected_count'), [(HTTPMethod.GET, False, 2), (HTTPMethod.POST, False, 1), (HTTPMethod.POST, True, 2)])
async def test_retry_requires_explicit_post_permission(transport, method, retry_post, expected_count):
    """GET 可恢复失败重试，POST 必须由具体只读 API 显式允许。"""
    responses, requests = transport
    responses.extend([(503, b'not exposed'), (200, b'ok')])
    if expected_count == 1:
        with pytest.raises(ApiTransportError):
            await BaseApi().request_text(method, 'https://example.test', retry_times=1, retry_post=retry_post)
    else:
        assert await BaseApi().request_text(method, 'https://example.test', retry_times=1, retry_post=retry_post) == 'ok'
    assert len(requests) == expected_count
    assert all(request[2]['ssl'] is True for request in requests)


async def test_size_failure_is_not_retried_or_exposed(transport):
    """超限响应确定失败，不重试或返回响应内容与目标地址。"""
    responses, requests = transport
    responses.append((200, b'secret-response'))
    with pytest.raises(ApiTransportError) as caught:
        await BaseApi().request_text(HTTPMethod.GET, 'https://secret.test', retry_times=2, response_max_bytes=2)
    assert len(requests) == 1
    assert 'secret' not in str(caught.value)


async def test_json_request_preserves_payload_and_rejects_invalid_json(transport):
    """JSON 参数保持原对象，解析失败仅返回安全协议错误。"""
    responses, requests = transport
    responses.extend([(200, b'{"code":0}'), (200, b'secret-page')])
    assert await BaseApi().request_json(HTTPMethod.POST, 'https://example.test', json_payload={'action': 'test'}) == {'code': 0}
    assert requests[0][2]['json'] == {'action': 'test'}
    with pytest.raises(ApiResponseError) as caught:
        await BaseApi().request_json(HTTPMethod.GET, 'https://example.test')
    assert 'secret' not in str(caught.value)


@pytest.mark.parametrize('fallback', ['utf-8', 'gbk'])
def test_decoding_respects_source_fallback(fallback):
    """全编码失败后的替换策略由来源指定，不能在迁移时被统一改变。"""
    body = b'\xff'
    assert BaseApi._decode(body, ('utf-8', 'gbk'), fallback) == body.decode(fallback, errors='replace')
