from typing import Any

from starlette import status

from core.dto.common_res import CommonRes
from core.status_enum import StatusEnum


class Response:
    @classmethod
    def success(cls, data: Any = None, message: str = 'success'):
        return CommonRes(data=data, message=message)

    @classmethod
    def error(cls, data: Any = None, message: str = 'success', code:StatusEnum=StatusEnum.error):
        return CommonRes(data=data, message=message, code=code.value)