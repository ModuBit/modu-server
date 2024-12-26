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
from typing import TypeVar, Dict, Any, Callable

T = TypeVar("T")


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
                key += "_"
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

    def as_dict(self):
        return self._data


def dict_get(
    dictionary: Dict[str, Any] | FrozenDictData, keys: str, default: T | None = None
) -> T | None:
    """
    支持字典的链式键值获取
    :param dictionary: 字典
    :param keys: 链式键
    :param default: 默认值
    :return: 字典中的值
    """

    try:
        # 将键链拆分为键列表
        keys_list = keys.split(".")
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


def dict_filter_none_values(dictionary: Dict) -> Dict:
    """
    过滤字典中的空值
    :param dictionary: 字典
    :return: 过滤后的字典
    """
    return {k: v for k, v in dict_empty_if_none(dictionary).items() if v is not None}


def dict_merge(
    dictionary_left: Dict, dictionary_right: Dict, filter_none_values: bool = True
) -> Dict:
    """
    合并两个字典
    :param dictionary_left: 左字典
    :param dictionary_right: 右字典
    :param filter_none_values: 是否过滤空值
    :return: 合并后的字典
    """
    if filter_none_values:
        dictionary_left = dict_filter_none_values(dictionary_left)
        dictionary_right = dict_filter_none_values(dictionary_right)
    return {
        **dict_empty_if_none(dictionary_left),
        **dict_empty_if_none(dictionary_right),
    }


def dict_exclude_keys(original_dict: Dict, keys_to_exclude: list | set):
    """
    将原字典中指定的 key 排除，生成新的字典
    :param original_dict: 原字典
    :param keys_to_exclude: 排除的 key 列表
    :return: 生成的新字典
    """
    return {
        key: value
        for key, value in dict_empty_if_none(original_dict).items()
        if key not in keys_to_exclude
    }


def dict_map_values(dictionary: Dict, value_map: Callable[[any, any], any]):
    """
    将原字典中的 value 映射为新的值
    :param dictionary: 原字典
    :param value_map: value 映射函数
    :return: 生成的新字典
    """
    return {
        key: value_map(key, value)
        for key, value in dict_empty_if_none(dictionary).items()
    }


def dict_map_keys(dictionary: Dict, key_map: Callable[[any], any]):
    """
    将原字典中的 key 映射为新的值
    :param dictionary: 原字典
    :param key_map: key 映射函数
    :return: 生成的新字典
    """
    return {
        key_map(key): value for key, value in dict_empty_if_none(dictionary).items()
    }


def dict_map_key_value(
    dictionary: Dict,
    key_map: Callable[[any], any],
    value_map: Callable[[any, any], any],
):
    """
    将原字典中的 key value 映射为新的值
    :param dictionary: 原字典
    :param key_map: key 映射函数
    :param value_map: value 映射函数
    :return: 生成的新字典
    """
    return {
        key_map(key): value_map(key, value)
        for key, value in dict_empty_if_none(dictionary).items()
    }


def dict_empty_if_none(dictionary: Dict | None) -> Dict | None:
    return {} if dictionary is None else dictionary
