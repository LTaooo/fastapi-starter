from typing import TypeVar

from fastapi import Depends

from core.di.container import Container

_Service = TypeVar('_Service')


def inject(service_type: type[_Service]):
    """声明请求期依赖，由容器提供进程内共享实例。"""

    async def resolve() -> _Service:
        """在事件循环中延迟解析服务，避免导入期加载配置及线程池初始化。"""
        return Container().get(service_type)

    return Depends(resolve)
