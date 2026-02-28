from typing import Optional, Any
import json
import redis.asyncio as redis
from utils.config import settings
from utils.logger import logger


class CacheService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache = {}
    
    async def connect(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using local cache only")
            self.redis_client = None

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        if key in self.local_cache:
            return self.local_cache[key]
        
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    data = json.loads(value)
                    self.local_cache[key] = data
                    return data
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        self.local_cache[key] = value
        
        if self.redis_client:
            try:
                json_value = json.dumps(value, ensure_ascii=False)
                await self.redis_client.setex(key, ttl, json_value)
            except Exception as e:
                logger.error(f"Redis set error: {e}")

    async def delete(self, key: str):
        self.local_cache.pop(key, None)
        
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")

    def clear_local_cache(self):
        self.local_cache.clear()


cache_service = CacheService()
