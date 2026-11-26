from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import Field

from config.base.base_nacos_config import BaseNacosConfig


class CrontabConfig(BaseNacosConfig):
    enable: bool = Field(description='是否开启', alias='crontab.enable', default=False)
    singleton: bool = Field(description='多实例时, 只在其中一个实例运行定时任务', alias='crontab.singleton', default=True)
    timezone: str = Field(description='定时任务时区', alias='crontab.timezone', default='Asia/Shanghai')

    @staticmethod
    def register_jobs(scheduler: AsyncIOScheduler) -> None:
        """注册定时任务，新增任务在此调用 scheduler.add_job。"""
        # 同步函数与协程函数都可传入，name 会出现在启动日志的任务清单中
        # 示例：
        # scheduler.add_job(lambda : print("hello"), 'interval', seconds=3, name='demo')
