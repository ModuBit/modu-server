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
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI
from loguru import logger

_pre_destroy_executors: list[Callable[[], None]] = []


def register_pre_destroy_executor(executor: Callable[[], None]):
    """
    注册应用关闭前的处理器
    :param executor: 处理器
    """
    global _pre_destroy_executors
    _pre_destroy_executors.append(executor)


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """
    FastAPI生命周期
    https://fastapi.tiangolo.com/advanced/events/
    :param fast_app: FastAPI
    """

    # start
    # 应用启动之后
    logger.info('==== application started ====')

    yield

    # shutdown
    # 应用关闭之前

    for executor in (_pre_destroy_executors or []):
        executor()

    logger.info('==== application will be shutdown ====')
