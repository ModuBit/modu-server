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

from typing import AsyncIterator, TypeVar

T = TypeVar('T')


async def merge_async_iterators(*iterators: AsyncIterator[T]) -> AsyncIterator[T]:
    """
    将多个异步迭代器合并成一个新的异步迭代器
    :param iterators: 待合并的异步迭代器
    :return:  新的异步迭代器
    """
    for iterator in filter(lambda it: it is not None, iterators):
        async for item in iterator:
            yield item


async def single_element_async_iterator(element: T) -> AsyncIterator[T]:
    """
    生成一个只包含一个元素的异步迭代器
    :param element: 元素
    :return: 异步迭代器
    """
    yield element
