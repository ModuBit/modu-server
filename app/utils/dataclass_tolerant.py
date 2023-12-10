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


def tolerant_dataclass(_cls=None, *, extra_ignore=False):
    def wrap(cls):
        # 保存原始 __init__
        orig_init = cls.__init__

        # 定义新的 __init__，它会忽略未定义的字段
        @wraps(orig_init)
        def new_init(self, *args, **kwargs):
            # 获取类中已定义的字段集合
            defined_fields = {field.name for field in fields(cls)}
            # 把传入的关键字参数分为已定义和未定义两组
            defined_kwargs = {k: v for k, v in kwargs.items() if k in defined_fields}
            extra_kwargs = {k: v for k, v in kwargs.items() if k not in defined_fields}

            # 调用原始的 __init__
            orig_init(self, *args, **defined_kwargs)

            # 如果需要，处理额外的关键字参数
            if extra_ignore:
                for key, value in extra_kwargs.items():
                    # 在这里，我们选择简单地忽略未定义的字段
                    # 但是你可以根据需要进行更复杂的处理
                    pass

        # 替换掉原来的 __init__ 方法
        cls.__init__ = new_init
        return cls

    # 支持没有括号的情况 @tolerant_dataclass
    if _cls is None:
        return wrap
    # 支持有括号的情况 @tolerant_dataclass(extra_ignore=True)
    return wrap(_cls)
