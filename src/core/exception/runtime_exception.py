from core.status_enum import StatusEnum


class RuntimeException(Exception):
    def __init__(self, message: str, code: StatusEnum = StatusEnum.error):
        self.message = message
        self.code = code

    def __str__(self):
        return self.message
