from typing import Callable

import yaml

from config.nacos_config import NacosConfig
from core.exception.runtime_exception import RuntimeException
from core.singleton_meta import SingletonMeta
from v2.nacos import (
    NacosNamingService,
    NacosConfigService,
    ClientConfigBuilder,
    GRPCConfig,
    ClientConfig,
    RegisterInstanceParam,
    ConfigParam,
)


class Nacos(metaclass=SingletonMeta):
    _config: NacosConfig
    _config_service: NacosConfigService
    _naming_service: NacosNamingService | None = None

    async def init(self, config: NacosConfig):
        """初始化Nacos客户端；未开启服务注册时不创建命名服务。"""
        self._config = config
        if not self._config.enable:
            return
        client_config = await self._get_client_config()
        await self._init_config_service(client_config)
        if self._config.register_enable:
            await self._init_naming_service(client_config)
            for service in self._config.get_services_data():
                await self.register_service(service)
        for listener_config in self._config.get_listener_data():
            await self.listener_config(listener_config.data_id, listener_config.listener)

    async def register_service(self, service: RegisterInstanceParam):
        """注册服务实例；未创建命名服务时拒绝调用。"""
        if self._naming_service is None:
            raise RuntimeException('Nacos服务注册未启用，无法注册服务')
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
            .log_dir(self._config.get_log_dir())
            .cache_dir(self._config.get_cache_dir())
            .namespace_id(self._config.namespace)
            .grpc_config(GRPCConfig(grpc_timeout=3000))
            .build()
        )
        return config

    async def get_config(self, config_param: ConfigParam) -> dict:
        if not self._config.enable:
            return {}
        data = await self._config_service.get_config(config_param)
        return yaml.safe_load(data or '')

    async def close(self):
        """关闭Nacos客户端；仅关闭实际创建过的服务。"""
        if not self._config.enable:
            return
        if self._naming_service is not None:
            await self._naming_service.shutdown()
            self._naming_service = None
        await self._config_service.shutdown()
