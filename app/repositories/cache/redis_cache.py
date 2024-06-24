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

from .cache import Cache


class RedisCache(Cache):
    def __init__(self, host: str, port: int, database: int, password: str):
        pool = redis.ConnectionPool(host=host, port=port, db=database, password=password, max_connections=10)
        self._redis = redis.Redis(connection_pool=pool)

    async def get(self, key: str) -> str:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, expire_seconds: int = 0):
        await self._redis.set(key, value, ex=expire_seconds)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def delete_all_with_prefix(self, key_prefix: str, batch_size: int = 10):
        keys = [key async for key in self._redis.scan_iter(match=f"{key_prefix}*")]
        for i in range(0, len(keys), batch_size):
            batch = keys[i:i + batch_size]
            await self._redis.delete(*batch)
