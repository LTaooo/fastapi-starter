"""命令行子命令的登记处：新增脚本时在这里加入命令类，并挂到根应用上。"""

import typer

from cli.commands.demo_command import DemoCommand
from cli.contract.cli_command import CliCommand

commands: tuple[CliCommand, ...] = (DemoCommand(),)


def register(app: typer.Typer) -> None:
    """把各子命令挂到根应用上，命令名取自命令类声明。"""
    for command in commands:
        app.command(name=command.name)(command.run)
