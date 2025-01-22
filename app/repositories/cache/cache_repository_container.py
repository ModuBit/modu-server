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

from typing import TypeVar

from config import app_config
from utils.dictionary import dict_get
from utils.lifespan import register_pre_destroy_executor
from .cache import Cache
from .redis_cache import RedisCache

_cache: dict[str, Cache] = {}
_cache_mapping = {
    "redis": RedisCache,
}


def get_cache(type: str | None = None) -> Cache:
    """
    根据配置中的缓存类型创建并返回一个缓存实例。

    :return: 缓存实例
    :raises ValueError: 如果缓存类型不受支持
    """

    global _cache
    global _cache_mapping

    cache_type = type or app_config.repository.cache.type
    if cache_type not in _cache_mapping:
        raise ValueError(f"Unsupported cache type: {cache_type}")

    cache = _cache.get(cache_type)
    if cache:
        return cache

    config = dict_get(app_config, f"repository.cache.{cache_type}")
    cache = _cache_mapping[cache_type](**config)
    _cache[cache_type] = cache

    register_pre_destroy_executor(cache.close)

    return cache
