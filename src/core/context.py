import contextvars


class Context:
    # 请求范围内的上下文变量
    __request_id_context = contextvars.ContextVar('request_id', default='')

    @classmethod
    def set_request_id(cls, request_id: str):
        cls.__request_id_context.set(request_id)

    @classmethod
    def get_request_id(cls) -> str:
        return cls.__request_id_context.get()
