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

from dataclasses import fields
from functools import wraps


def tolerant(_cls=None):
    """
    对dataclass做宽容处理
    如果初始化时传入了未定义的字段值则忽略
    而不是抛出 TypeError: __init__() got an unexpected keyword argument
    """

    def wrap(cls):
        # 保存原始 __init__
        orig_init = cls.__init__

        # 定义新的 __init__，忽略未定义的字段
        @wraps(orig_init)
        def __new_init__(self, *args, **kwargs):
            # 获取类中已定义的字段集合
            defined_fields = {field.name for field in fields(cls)}
            defined_kwargs = {k: v for k, v in kwargs.items() if k in defined_fields}
            for k in defined_fields - set(defined_kwargs.keys()):
                defined_kwargs[k] = None

            # 调用原始的 __init__
            orig_init(self, *args, **defined_kwargs)

        # 替换掉原来的 __init__ 方法
        cls.__init__ = __new_init__
        return cls

    # 支持没有括号的情况 @tolerant
    if _cls is None:
        return wrap
    # 支持有括号的情况 @tolerant()
    return wrap(_cls)
