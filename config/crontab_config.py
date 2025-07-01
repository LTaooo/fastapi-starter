from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import Field

from config.app_config import AppConfig
from config.base.base_nacos_config import BaseNacosConfig
from core.config import Config
from core.logger import Logger


# noinspection PyMethodMayBeStatic
class CrontabConfig(BaseNacosConfig):
    enable: bool = Field(description='是否开启', alias='crontab.enable', default=False)
    singleton: bool = Field(description='多实例时, 只在其中一个实例运行定时任务', alias='crontab.singleton', default=True)

    def get_singleton_key(self):
        return f'{Config.get(AppConfig).app_name}_crontab_lock'

    async def register_jobs(self, scheduler: AsyncIOScheduler):
        """
        注册定时任务
        """
        if not self.enable:
            return

        scheduler.add_job(lambda: Logger.get().info('test crontab'), 'interval', minutes=1, name='测试定时任务')
