from typing import Callable

from config.nacos_config import NacosConfig
from core.singleton_meta import SingletonMeta
from v2.nacos import NacosNamingService, NacosConfigService, ClientConfigBuilder, GRPCConfig, ClientConfig, RegisterInstanceParam


class Nacos(metaclass=SingletonMeta):
    _config: NacosConfig
    _config_service: NacosConfigService
    _naming_service: NacosNamingService

    async def init(self, config: NacosConfig):
        self._config = config
        if not self._config.enable:
            return
        client_config = await self._get_client_config()
        await self._init_config_service(client_config)
        await self._init_naming_service(client_config)
        for service in self._config.get_services_data():
            await self.register_service(service)
        for listener_config in self._config.get_listener_data():
            await self.listener_config(listener_config.data_id, listener_config.listener)

    async def register_service(self, service: RegisterInstanceParam):
        await self._naming_service.register_instance(service)

    async def listener_config(self, data_id: str, listener: Callable):
        await self._config_service.add_listener(data_id, self._config.group, listener)

    async def _init_config_service(self, client_config: ClientConfig):
        self._config_service = await NacosConfigService.create_config_service(client_config)

    async def _init_naming_service(self, client_config: ClientConfig):
        self._naming_service = await NacosNamingService.create_naming_service(client_config)

    async def _get_client_config(self) -> ClientConfig:
        config = (
            ClientConfigBuilder()
            .username(self._config.username)
            .password(self._config.password)
            .server_address(self._config.server_addresses)
            .log_level(self._config.log_level)
            .log_dir(self._config.log_dir)
            .namespace_id(self._config.namespace)
            .grpc_config(GRPCConfig(grpc_timeout=3000))
            .build()
        )
        return config

    async def close(self):
        if not self._config.enable:
            return
        await self._naming_service.shutdown()
        await self._config_service.shutdown()
