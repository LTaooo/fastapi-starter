from config.app_config import AppConfig
from core.config import Config

if Config.get(AppConfig).is_dev():
    from app.queues import demo_queue as demo_queue
