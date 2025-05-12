from nacos import NacosClient

from config.nacos_config import NacosConfig
from core.config import Config
from core.singleton_meta import SingletonMeta


class Nacos(metaclass=SingletonMeta):
    def __init__(self):
        self.config: NacosConfig = Config.get(NacosConfig)
        if not self.config.enable:
            return
        self.client: NacosClient = NacosClient(self.config.server_addresses, namespace=self.config.namespace)
        self.register_service()

    def register_service(self):
        for service in self.config.services:
            self.client.add_naming_instance(
                service_name=service.name,
                ip=service.ip,
                port=3306,
                group_name=self.config.group,
                healthy=True,
                weight=1.0,
            )

    def unregister_service(self):
        if not self.config.enable:
            return
        for service in self.config.services:
            self.client.remove_naming_instance(service.name, service.ip, service.port)
