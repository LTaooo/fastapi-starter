from redis.asyncio import Redis as AsyncIORedis, ConnectionPool
from config.redis_config import RedisConfig
from core.config import Config
from core.logger import Logger
from core.singleton_meta import SingletonMeta


class Redis(metaclass=SingletonMeta):
    def __init__(self):
        self.config: RedisConfig = Config().get(RedisConfig)
        self.pool: ConnectionPool | None = None
        self.redis: AsyncIORedis | None = None

    def is_enable(self) -> bool:
        return self.config.enable

    def _get_client(self) -> AsyncIORedis:
        if self.redis is None:
            self.pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.connection_pool,
                health_check_interval=60,
                retry_on_timeout=True,
                decode_responses=True,
            )
            self.redis = AsyncIORedis(connection_pool=self.pool)
        return self.redis

    async def connect(self):
        if not self.config.enable:
            return
        await self._get_client().ping()
        Logger.get().info('Redis连接成功')

    def get_instance(self) -> AsyncIORedis:
        return self._get_client()

    async def disconnect(self):
        if self.redis is not None:
            await self.redis.aclose()
            self.redis = None
        if self.pool is not None:
            await self.pool.disconnect()
            self.pool = None
