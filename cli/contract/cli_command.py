from abc import ABC, abstractmethod
from typing import Any, ClassVar


class CliCommand(ABC):
    """命令行子命令的公共契约：声明命令名，并作为可调用目标交给应用绑定参数。"""

    name: ClassVar[str]

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> None:
        """执行子命令；具体命令行参数由各子命令的 run 签名声明，基类以任意参数占位以兼容不同签名。"""
        raise NotImplementedError
