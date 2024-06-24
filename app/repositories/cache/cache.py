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
import inspect
from abc import ABC, abstractmethod
from functools import wraps
from typing import TypeVar, Callable, Generic, Awaitable

T = TypeVar('T')

none_content = 'None'


def func_bound_values(func, *args, **kwargs):
    """
    将 *args, **kwargs 绑定到func的参数上
    :param func: 函数
    :param args: args
    :param kwargs: kwargs
    :return: {key: func参数名, value: func参数值}
    """
    # 获取函数参数名列表
    sig = inspect.signature(func)
    # 函数参数元数据
    params = sig.parameters
    # 将所有位置参数和关键字参数统一存入字典
    bound_values = sig.bind_partial(*args, **kwargs).arguments
    # 将 bound_values 和 params 中的默认值合并
    bound_values.update({k: v.default for k, v in params.items() if k not in bound_values})
    return bound_values


class Cache(ABC):
    """
    缓存基类
    """

    @abstractmethod
    async def get(self, key: str) -> str:
        """
        获取缓存
        :param key: 缓存健
        :return: 缓存内容
        """
        raise NotImplementedError()

    @abstractmethod
    async def set(self, key: str, value: str, expire_seconds: int = 0):
        """
        设置缓存
        :param key: 缓存健
        :param value: 缓存内容
        :param expire_seconds: 过期时间
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, key: str):
        """
        删除缓存
        :param key: 缓存健
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete_all_with_prefix(self, key_prefix: str, batch_size: int = 10):
        """
        删除所有前缀缓存
        :param key_prefix: 缓存健
        :param batch_size: 批量删除数量
        """
        raise NotImplementedError()


class CacheDecorator(Generic[T]):
    """
    缓存Decorator
    """

    def __init__(self,
                 cache: Cache,
                 serialize: Callable[[T], str],
                 deserialize: Callable[[str], T],
                 default_expire_seconds: int = 3600,
                 allow_none_values: bool = False, ):
        """
        缓存Decorator
        :param cache: 缓存实例
        :param serialize: 序列化方法
        :param deserialize: 反序列化方法
        :param default_expire_seconds: 默认过期时间（TTL，相对时间）
        :param allow_none_values: 是否缓存None，可以有效防止缓存击穿，默认不缓存
        """
        self._cache = cache
        self._serialize = serialize
        self._deserialize = deserialize
        self._default_expire_time = default_expire_seconds
        self._allow_none_values = allow_none_values

    def async_cacheable(self, key_generator: Callable[..., str], expire_seconds: int = None):
        """
        在调用方法时优先取缓存值，若无缓存则调用原方法，并将方法返回值缓存
        :param key_generator: 缓存key生成方法
        :param expire_seconds: 过期时间，缺省使用默认值
        """

        def decorator(func: Callable[..., Awaitable[T]], ):
            # noinspection PyBroadException
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 方法参数值
                bound_values = func_bound_values(func, *args, **kwargs)

                # 缓存中的值
                cache_key = key_generator(**bound_values)
                cached_content = await self._cache.get(cache_key, )
                if cached_content is not None:
                    # 缓存中有值
                    try:
                        # 缓存了None
                        if none_content == cached_content:
                            return None
                    except Exception as ex:
                        pass
                    # 返回缓存中的值
                    return self._deserialize(cached_content)

                # 调用原方法
                origin_value = await func(*args, **kwargs)

                if origin_value is None and not self._allow_none_values:
                    # 不缓存None
                    return None

                # 存入缓存
                cache_value = self._serialize(origin_value) if origin_value is not None else none_content
                await self._cache.set(cache_key, cache_value, expire_seconds or self._default_expire_time)

                return origin_value

            return wrapper

        return decorator

    def async_cache_put(self, key_generator: Callable[..., str], expire_seconds: int = None):
        """
        在调用方法时总是调用原方法，并将方法返回值缓存
        :param key_generator: 缓存key生成方法
        :param expire_seconds: 过期时间，缺省使用默认值
        """

        def decorator(func: Callable[..., Awaitable[T]], ):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 调用原方法
                origin_value = await func(*args, **kwargs)

                if origin_value is None and not self._allow_none_values:
                    # 不缓存None
                    return None

                # 方法参数值
                bound_values = func_bound_values(func, *args, **kwargs)

                # 存入缓存
                cache_key = key_generator(**bound_values)
                cache_value = self._serialize(origin_value) if origin_value is not None else none_content
                await self._cache.set(cache_key, cache_value, expire_seconds or self._default_expire_time)

                # 返回原方法执行结果
                return origin_value

            return wrapper

        return decorator

    def async_cache_evict(self, key_generator: Callable[..., str], expire_seconds: int = None):
        """
        在调用方法时总是调用原方法，并将对应的缓存删除
        :param key_generator: 缓存key生成方法
        :param expire_seconds: 过期时间，缺省使用默认值
        """

        def decorator(func: Callable[..., Awaitable[T]], ):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 调用原方法
                origin_value = await func(*args, **kwargs)

                # 方法参数值
                bound_values = func_bound_values(func, *args, **kwargs)

                # 删除缓存中的值
                cache_key = key_generator(**bound_values)
                await self._cache.delete(cache_key)

                return origin_value

            return wrapper

        return decorator

    def async_cache_evict_with_prefix(self, key_prefix_generator: Callable[..., str], expire_seconds: int = None):
        """
        在调用方法时总是调用原方法，并将对应前缀的缓存全部删除
        :param key_prefix_generator: 缓存key前缀生成方法
        :param expire_seconds: 过期时间，缺省使用默认值
        """

        def decorator(func: Callable[..., Awaitable[T]], ):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 调用原方法
                origin_value = await func(*args, **kwargs)

                # 方法参数值
                bound_values = func_bound_values(func, *args, **kwargs)

                # 删除缓存中的值
                cache_key = key_prefix_generator(**bound_values)
                await self._cache.delete_all_with_prefix(cache_key)

                return origin_value

            return wrapper

        return decorator


class CacheDecoratorBuilder:
    """
    缓存Decorator构造
    """

    def __init__(self, cache: Cache):
        """
        缓存Decorator构造
        :param cache: 缓存实例
        """
        self.cache = cache

    def build(self,
              serialize: Callable[[T], str],
              deserialize: Callable[[str], T],
              default_expire_seconds: int = 3600,
              allow_none_values: bool = False,
              ) -> CacheDecorator:
        """
        构造CacheManager
        :param serialize: 序列化方法
        :param deserialize: 反序列化方法
        :param default_expire_seconds: 默认过期时间（TTL，相对时间）
        :param allow_none_values: 是否缓存None，可以有效防止缓存击穿，默认不缓存
        :return:
        """
        return CacheDecorator(self.cache, serialize, deserialize, default_expire_seconds, allow_none_values, )
