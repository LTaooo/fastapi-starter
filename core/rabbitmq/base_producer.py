from abc import ABC

from config.app_config import AppConfig
from core.config import Config


class BaseProducer(ABC):
    @classmethod
    def get_routing_key(cls) -> str:
        return Config.get(AppConfig).app_name + '_task_routing_key'
