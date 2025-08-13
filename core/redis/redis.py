from redis.asyncio import Redis as AsyncIORedis, ConnectionPool
from config.redis_config import RedisConfig
from core.config import Config
from core.logger import Logger
from core.singleton_meta import SingletonMeta


class Redis(metaclass=SingletonMeta):
    def __init__(self):
        config = Config().get(RedisConfig)
        self.pool = ConnectionPool(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            max_connections=config.connection_pool,
            decode_responses=True,
        )
        self.redis = AsyncIORedis(connection_pool=self.pool)

    async def connect(self):
        await self.redis.ping()
        Logger.get().info('Redis连接成功')

    def get_instance(self) -> AsyncIORedis:
        return self.redis

    async def disconnect(self):
        if self.redis:
            await self.redis.aclose()
        if self.pool:
            await self.pool.disconnect()
