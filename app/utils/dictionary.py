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

from typing import TypeVar, Optional

T = TypeVar('T')


def dict_get(dictionary: dict, keys: str, default: Optional[T] = None) -> T | None:
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
            dictionary = dictionary[key]
    except (KeyError, AttributeError, TypeError):
        # 如果在任何一级找不到键或者当前值不是字典，则返回默认值
        return default
    return dictionary
