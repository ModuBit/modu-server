"""
Copyright 2024 Maner·Fan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import redis.asyncio as redis
from loguru import logger

from .cache import Cache


class RedisCache(Cache):
    def __init__(self, host: str, port: int, database: int, password: str):
        self._host = host
        self._port = port
        self._database = database

        pool = redis.ConnectionPool(host=host, port=port, db=database, password=password, max_connections=10)
        self._redis = redis.Redis(connection_pool=pool)
        logger.info('=== create redis({}) {}:{}/{} ===', id(self), host, port, database)

    async def get(self, key: str) -> str | bytes | None:
        return await self._redis.get(key)

    async def mget(self, keys: list[str]) -> list[str | bytes | None]:
        if not keys:
            return []
        return await self._redis.mget(keys)

    async def set(self, key: str, value: str | bytes, expire_seconds: int = 0):
        await self._redis.set(key, value, ex=expire_seconds)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def delete_all_key_pattern(self, key_pattern: str, batch_size: int = 10):
        keys = [key async for key in self._redis.scan_iter(match=key_pattern)]
        for i in range(0, len(keys), batch_size):
            batch = keys[i:i + batch_size]
            await self._redis.delete(*batch)

    async def close(self):
        logger.info('=== close redis({}) {}:{}/{} ===', id(self), self._host, self._port, self._database)
        await self._redis.close()
