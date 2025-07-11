from typing import Any

from config.app_config import AppConfig
from core.config import Config


def examples(e: list[Any]) -> list[Any] | None:
    return None if Config.get(AppConfig).is_prod() else e
