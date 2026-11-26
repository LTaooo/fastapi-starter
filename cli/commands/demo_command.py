from typing import Annotated

import typer
from pydantic import BaseModel, Field

from cli.contract.cli_command import CliCommand
from config.app_config import AppConfig
from core.config import Config
from core.script_runner import run_script


class DemoCommand(CliCommand):
    """演示命令行骨架的最小命令。"""

    name = 'demo'

    def run(
        self,
        message: Annotated[str, typer.Option('--message', help='回显内容')] = 'hello',
    ) -> None:
        """在应用生命周期内读取配置并回显，结果以一行 JSON 打印到标准输出。"""
        exit_code = run_script(lambda: self._echo(message), '演示命令')
        if exit_code != 0:
            raise typer.Exit(code=exit_code)

    async def _echo(self, message: str) -> int:
        """输出应用名称、环境与回显内容，固定返回 0。"""
        app_config = Config.get(AppConfig)
        payload = DemoResponse(app=app_config.app_name, env=app_config.app_env.value, message=message)
        print(payload.model_dump_json())
        return 0


class DemoResponse(BaseModel):
    """demo 子命令的标准输出响应。"""

    app: str = Field(description='应用名称')
    env: str = Field(description='运行环境')
    message: str = Field(description='回显内容')
