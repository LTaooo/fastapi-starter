import asyncio
import json
from http import HTTPMethod, HTTPStatus
from typing import Any

import aiohttp

from core.http.http_constants import HTTP_CHUNK_SIZE, RECOVERABLE_HTTP_STATUSES, RETRY_BACKOFF_SECONDS
from core.http.api_exception import ApiResponseError, ApiTransportError
from core.logger import Logger


class _RecoverableRequestError(RuntimeError):
    """仅用于内部区分可恢复的 HTTP 故障。"""


class BaseApi:
    """外部接口共用的无状态 HTTP 传输，来源协议由具体 API 类实现。"""

    async def request_text(
        self,
        method: HTTPMethod,
        url: str,
        *,
        timeout_seconds: float = 15,
        params: dict[str, str] | None = None,
        form: dict[str, str] | None = None,
        json_payload: Any = None,
        raw_body: str | bytes | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        retry_times: int = 0,
        retry_post: bool = False,
        response_max_bytes: int | None = None,
        encodings: tuple[str, ...] = ('utf-8',),
        fallback_encoding: str | None = None,
        trust_env: bool = False,
    ) -> str:
        """发送请求并按指定编码读取文本，失败不暴露 URL、凭据或原始内容。

        :param retry_post: 仅只读且可安全重复的 POST 查询可显式开启；其他 POST 不自动重试。
        :param retry_times: 首次请求以外的重试上限，仅适用于网络错误和白名单状态。
        :param fallback_encoding: 全部严格解码失败后使用的替换编码；未指定时使用最后一个编码。
        :param raw_body: 原始请求体，与 form、json_payload 互斥，用于保留第三方既有协议。
        """
        self._validate_options(form, json_payload, raw_body, encodings, timeout_seconds, retry_times, response_max_bytes)
        retries = retry_times if method != HTTPMethod.POST or retry_post else 0
        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        options = {'params': params, 'data': raw_body if raw_body is not None else form, 'json': json_payload, 'headers': headers, 'proxy': proxy, 'ssl': True}
        async with aiohttp.ClientSession(timeout=timeout, trust_env=trust_env) as session:
            for attempt in range(retries + 1):
                try:
                    body = await self._request_once(session, method, url, options, response_max_bytes)
                    return self._decode(body, encodings, fallback_encoding)
                except _RecoverableRequestError as exc:
                    if attempt == retries:
                        raise ApiTransportError(str(exc)) from None
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
        raise ApiTransportError('外部接口请求失败')

    async def request_json(
        self,
        method: HTTPMethod,
        url: str,
        *,
        timeout_seconds: float = 15,
        params: dict[str, str] | None = None,
        form: dict[str, str] | None = None,
        json_payload: Any = None,
        raw_body: str | bytes | None = None,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        retry_times: int = 0,
        retry_post: bool = False,
        response_max_bytes: int | None = None,
        encodings: tuple[str, ...] = ('utf-8',),
        fallback_encoding: str | None = None,
        trust_env: bool = False,
    ) -> Any:
        """解析外部 JSON，不依赖响应 Content-Type；格式错误不返回原始页面。"""
        body = await self.request_text(
            method,
            url,
            timeout_seconds=timeout_seconds,
            params=params,
            form=form,
            json_payload=json_payload,
            raw_body=raw_body,
            headers=headers,
            proxy=proxy,
            retry_times=retry_times,
            retry_post=retry_post,
            response_max_bytes=response_max_bytes,
            encodings=encodings,
            fallback_encoding=fallback_encoding,
            trust_env=trust_env,
        )
        try:
            return json.loads(body)
        except (json.JSONDecodeError, ValueError):
            raise ApiResponseError('外部接口返回非 JSON 内容') from None

    @staticmethod
    def _validate_options(
        form: dict[str, str] | None,
        json_payload: Any,
        raw_body: str | bytes | None,
        encodings: tuple[str, ...],
        timeout_seconds: float,
        retry_times: int,
        response_max_bytes: int | None,
    ) -> None:
        """在请求前拒绝互斥请求体与无效的网络选项。"""
        if sum(value is not None for value in (form, json_payload, raw_body)) > 1:
            raise ValueError('form、json_payload、raw_body 不能同时设置')
        if not encodings:
            raise ValueError('encodings 不能为空')
        if timeout_seconds <= 0 or retry_times < 0 or (response_max_bytes is not None and response_max_bytes <= 0):
            raise ValueError('超时和响应大小必须为正，重试次数不能为负')

    async def _request_once(
        self, session: aiohttp.ClientSession, method: HTTPMethod, url: str, options: dict[str, Any], response_max_bytes: int | None
    ) -> bytes:
        """单次 HTTP 请求；确定性 HTTP 失败和超限响应不重试。"""
        try:
            async with session.request(method, url, **options) as response:
                self._validate_response(response)
                if response.status >= HTTPStatus.BAD_REQUEST:
                    Logger.get().warning(
                        '外部接口响应异常 api={} method={} status={} content_length={}',
                        type(self).__name__,
                        method,
                        response.status,
                        response.content_length,
                    )
                if response.status >= HTTPStatus.BAD_REQUEST:
                    message = f'{method} 上游返回状态 {response.status}'
                    if response.status in RECOVERABLE_HTTP_STATUSES:
                        raise _RecoverableRequestError(message)
                    raise ApiTransportError(message)
                return await self._read_limited(response, response_max_bytes)
        except (aiohttp.ClientError, TimeoutError, OSError):
            raise _RecoverableRequestError(f'{method} 网络请求失败') from None

    def _validate_response(self, response: aiohttp.ClientResponse) -> None:
        """供具体 API 校验上游响应，默认不增加协议限制。"""

    @staticmethod
    async def _read_limited(response: aiohttp.ClientResponse, limit: int | None) -> bytes:
        """受限读取响应；未设上限时保持原调用方的完整读取行为。"""
        if limit is not None and response.content_length is not None and response.content_length > limit:
            raise ApiTransportError('上游响应体超过大小上限')
        body = bytearray()
        async for chunk in response.content.iter_chunked(HTTP_CHUNK_SIZE):
            body.extend(chunk)
            if limit is not None and len(body) > limit:
                raise ApiTransportError('上游响应体超过大小上限')
        return bytes(body)

    @staticmethod
    def _decode(body: bytes, encodings: tuple[str, ...], fallback_encoding: str | None) -> str:
        """依次严格解码，全部失败后按调用方指定编码替换非法字节。"""
        for encoding in encodings:
            try:
                return body.decode(encoding)
            except UnicodeDecodeError:
                continue
        return body.decode(fallback_encoding or encodings[-1], errors='replace')
