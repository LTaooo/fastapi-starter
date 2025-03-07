from typing import Any

from starlette import status

from core.dto.common_res import CommonRes


class Response:
    @classmethod
    def success(cls, data: Any = None, message: str = 'success'):
        return CommonRes(data=data, message=message)

    @classmethod
    def error(cls, data: Any = None, message: str = 'success', code:status=status.HTTP_500_INTERNAL_SERVER_ERROR):
        return CommonRes(data=data, message=message, code=code)