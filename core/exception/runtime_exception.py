from starlette import status


class RuntimeException(Exception):
    def __init__(self, message: str, code: status = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code

    def __str__(self):
        return self.message

