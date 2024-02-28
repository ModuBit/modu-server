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

import importlib
import pkgutil
from typing import TypeVar, Type

T = TypeVar('T')


def load_classes(package_name: str, cls_type: Type[T],
                 recursive: bool = False, max_depth: int = -1) -> list[Type[T]]:
    """
    扫描指定包，并加载模块中指定类
    :param package_name: 需要扫描的包含
    :param cls_type: 需要扫描的类
    :param recursive: 是否递归
    :param max_depth: 递归最大深度
    :return: 扫描到的指定类
    """
    return _load_classes(package_name, cls_type, recursive, max_depth)


def _load_classes(package_name: str, cls_type: Type[T],
                  recursive: bool = False, max_depth: int = -1, current_depth: int = 0, ) -> list[Type[T]]:
    """
    扫描指定包，并加载模块中指定类
    :param package_name: 需要扫描的包含
    :param cls_type: 需要扫描的类
    :param recursive: 是否递归
    :param max_depth: 递归最大深度
    :param current_depth: 当前递归深度
    :return: 扫描到的指定类
    """

    cls_types: list[Type[T]] = []

    # 加载包
    package = importlib.import_module(package_name)

    # 遍历包中的所有模块
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        if is_pkg and recursive and (max_depth < 0 or current_depth < max_depth):
            # 递归加载子包
            cls_types += _load_classes(module_name, cls_type, recursive, max_depth, current_depth + 1)
            continue

        module = importlib.import_module(module_name)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            # 检查是否是cls_type的子类 (排除cls_type自身)
            if isinstance(attribute, type) and issubclass(attribute, cls_type) and attribute is not cls_type:
                cls_types.append(attribute)

    return cls_types
