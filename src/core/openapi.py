from typing import Callable


def openapi(func: Callable[..., dict]) -> Callable[..., dict]:
    """
    Customize OpenAPI schema.
    这里移除422文档
    """

    def wrapper(*args, **kwargs) -> dict:
        """Wrapper."""
        res = func(*args, **kwargs)
        for _, method_item in res.get('paths', {}).items():
            for _, param in method_item.items():
                responses = param.get('responses')
                # remove default 422 - the default 422 schema is HTTPValidationError
                if '422' in responses and responses['422']['content']['application/json']['schema']['$ref'].endswith('HTTPValidationError'):
                    del responses['422']
        return res

    return wrapper
