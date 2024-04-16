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

import keyword
import typing
from collections import abc
from types import MappingProxyType
from typing import TypeVar, Dict, Any

T = TypeVar('T')


class FrozenDictData:
    """
    使dict可以像dataclass一样通过属性名进行访问
    同时继续保留dict的特性
    """

    def __new__(cls, obj):
        if obj is None:
            return None
        elif isinstance(obj, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(obj, abc.MutableSequence):
            return [cls(item) for item in obj]
        else:
            return obj

    def __init__(self, data: typing.Mapping):
        __data = {}
        # 处理关键字
        for key, value in data.items():
            if keyword.iskeyword(key):
                key += '_'
            __data[key] = value
        self._data = MappingProxyType(__data)

    # ↓↓↓ 模拟 data class ↓↓↓

    def __dir__(self):
        return self._data.keys()

    def __getattr__(self, name):
        try:
            return getattr(self._data, name)
        except AttributeError:
            return FrozenDictData(self._data.get(name, None))

    # ↑↑↑ 模拟 data class ↑↑↑

    # ↓↓↓ 模拟 dict ↓↓↓

    def keys(self):
        return self.__dir__()

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __contains__(self, item):
        return item in self.keys()

    # ↑↑↑ 模拟 dict ↑↑↑

    def __dict__(self):
        return self._data


def dict_get(dictionary: Dict[str, Any] | FrozenDictData, keys: str, default: T | None = None) -> T | None:
    """
    支持字典的链式键值获取
    :param dictionary: 字典
    :param keys: 链式键
    :param default: 默认值
    :return: 字典中的值
    """

    try:
        # 将键链拆分为键列表
        keys_list = keys.split('.')
        # 遍历键列表，逐层深入字典
        for key in keys_list:
            if dictionary is None or key not in dictionary:
                return default
            dictionary = dictionary[key]
    except (KeyError, AttributeError, TypeError) as e:
        print(f"Caught an exception: {type(e).__name__}: {e}")
        # 如果在任何一级找不到键或者当前值不是字典，则返回默认值
        return default
    return dictionary
