import io
import sys
from typing import Annotated, TextIO

import typer

from cli.registry import register
from core.logger import Logger

# 命令行默认只把告警与报错写到控制台，结果 JSON 之外不产生干扰输出。
_QUIET_LEVEL = 'WARNING'


class BaseCli:
    """命令行应用的构建与运行入口：保留分组形态，登记子命令，统管输出流与日志出口。"""

    def __init__(self) -> None:
        self._app = typer.Typer(add_completion=False, rich_markup_mode=None, pretty_exceptions_enable=False)
        self._app.callback()(self._main)
        register(self._app)

    def _main(
        self,
        verbose: Annotated[bool, typer.Option('--verbose', help='打印过程日志；默认只输出结果 JSON 与告警')] = False,
    ) -> None:
        """fastapi-starter 运维脚本入口，结果以 JSON 输出。"""
        if verbose:
            # 传空取消控制台级别覆盖，回到配置级别
            Logger.use_console_level(None)

    def run(self, argv: list[str] | None = None) -> int:
        """运行命令行应用并返回进程退出码；argv 为空时取进程参数。"""
        _use_utf8(sys.stdout)
        _use_utf8(sys.stderr)
        Logger.use_stderr()
        Logger.use_console_level(_QUIET_LEVEL)
        try:
            self._app(args=argv)
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 0
        return 0


def _use_utf8(stream: TextIO) -> None:
    """把文本流固定为 UTF-8，避免控制台代码页把中文写成非 UTF-8 字节。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding='utf-8')
