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

import asyncio
import datetime
import functools
import json

from fastapi import Request
from loguru import logger
from sqlalchemy import text, DateTime, UUID, String, AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

from .database import Database, BasePO
from .type_decorator import Bool2SmallInt


def get_request_id(request: Request):
    return id(request)


class PostgresDatabase(Database):
    """
    PostgreSQL连接
    """

    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self._host = host
        self._port = port
        self._database = database

        self._engine = create_async_engine(
            f'postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}',
            json_serializer=functools.partial(json.dumps, ensure_ascii=False),
            # 指定连接池类
            poolclass=AsyncAdaptedQueuePool,
            # 连接池大小
            pool_size=10,
            # 连接池中的连接最大闲置时间，超过这个时间的闲置连接将被回收
            pool_timeout=30,
            # 空连接回收时间
            pool_recycle=3600,
            # 每个连接被使用前预检
            pool_pre_ping=True,
        )
        # async_scoped_session
        self._async_session_factory = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )
        logger.info('=== create postgresql({}) {}:{}/{} ===', id(self), host, port, database)

    def close(self):
        logger.info('=== close postgresql({}) {}:{}/{} ===', id(self), self._host, self._port, self._database)
        self._async_session_factory.close_all()
        loop = asyncio.get_event_loop()
        future = asyncio.run_coroutine_threadsafe(self._engine.dispose(), loop)
        future.result()

    def __del__(self):
        self.close()

    def get_async_session(self) -> AsyncSession:
        return self._async_session_factory()


class PostgresBasePO(BasePO):
    """
    PostgreSQL通用模型
    """

    # 标识为抽象类，防止sqlalchemy将该类直接映射到数据库表
    __abstract__ = True

    # 主键ID
    id: Mapped[str] = mapped_column(UUID, primary_key=True,
                                    server_default=text('uuid_generate_v4()'),
                                    comment='主键ID')
    # 全局ID
    uid: Mapped[str] = mapped_column(String(32), nullable=False,
                                     default=BasePO.uid_generate,
                                     comment='UID')
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 server_default=text('CURRENT_TIMESTAMP(0)'),
                                                 comment='创建时间')
    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 server_default=text('CURRENT_TIMESTAMP(0)'),
                                                 onupdate=text('CURRENT_TIMESTAMP(0)'),
                                                 comment='更新时间')

    is_deleted: Mapped[bool] = mapped_column(Bool2SmallInt, nullable=False,
                                             server_default=text('0'),
                                             comment='是否已删除')
