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

import datetime
import json

from sqlalchemy import text, DateTime, UUID, create_engine, QueuePool, String
from sqlalchemy.orm import Mapped, mapped_column, scoped_session, sessionmaker, Session

from .database import Database, BasePO


class PostgresDatabase(Database):
    """
    PostgreSQL连接
    """

    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self._engine = create_engine(
            f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}',
            json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
            # 指定连接池类
            poolclass=QueuePool,
            # 连接池大小
            pool_size=10,
            # 连接池中的连接最大闲置时间，超过这个时间的闲置连接将被回收
            pool_timeout=30,
            # 空连接回收时间
            pool_recycle=3600,
            # 每个连接被使用前预检
            pool_pre_ping=True,
        )
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def get_session(self) -> Session:
        return self._session_factory()


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
