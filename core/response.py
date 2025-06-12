from typing import Any

from core.context import Context
from core.dto.common_res import CommonRes
from core.status_enum import StatusEnum


class Response:
    @classmethod
    def success(cls, data: Any = None, message: str = 'success'):
        return CommonRes(data=data, message=message, request_id=Context.get_request_id())

    @classmethod
    def error(
        cls,
        message: str = 'error',
        data: Any = None,
        code: StatusEnum = StatusEnum.error,
    ):
        return CommonRes(data=data, message=message, code=code.value, request_id=Context.get_request_id())
