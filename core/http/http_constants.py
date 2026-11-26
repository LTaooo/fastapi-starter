from http import HTTPStatus
from typing import Final

# 单次读取响应流的字节数。
HTTP_CHUNK_SIZE: Final = 65_536
# 可恢复请求失败的基础退避秒数。
RETRY_BACKOFF_SECONDS: Final = 0.5
# 允许受控重试的限流及瞬时服务端状态。
RECOVERABLE_HTTP_STATUSES: Final = frozenset(
    {HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE, HTTPStatus.GATEWAY_TIMEOUT}
)
