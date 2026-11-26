class ApiTransportError(RuntimeError):
    """外部 HTTP 传输失败，消息不包含地址、凭据、请求体或原始响应。"""


class ApiResponseError(RuntimeError):
    """外部响应不满足协议格式，调用方负责转换为业务错误。"""
