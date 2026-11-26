from core.status_enum import StatusEnum


class BizException(Exception):
    """业务失败异常；message 由全局异常处理原样返回给调用方，只写可对外展示的文案。"""

    def __init__(self, message: str, code: StatusEnum = StatusEnum.error):
        self.message = message
        self.code = code

    def __str__(self):
        return self.message
