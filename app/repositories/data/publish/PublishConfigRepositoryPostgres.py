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

from sqlalchemy import TypeDecorator, PrimaryKeyConstraint, String, text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from repositories.data.database import with_async_session
from repositories.data.postgres_database import PostgresBasePO
from repositories.data.publish.PublishConfigRepository import PublishConfigRepository
from repositories.data.publish.publish_config import PublishConfigTargetType, PublishConfigStatus, PublishConfig


class PublishConfigRepositoryPostgres(PublishConfigRepository):
    """
    发布配置数据存储的PostgreSQL实现
    """

    @with_async_session
    async def add_or_update(self, publish_config: PublishConfig, session: AsyncSession) -> PublishConfig:
        pass


class Dict2Json(TypeDecorator):
    impl = JSONB

    cache_ok = False

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value


class PublishConfigPO(PostgresBasePO):
    """
    配置发布
    """

    __tablename__ = 'modu_publish_configs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    target_type: Mapped[PublishConfigTargetType] = mapped_column(
        Enum(PublishConfigTargetType, native_enum=False), nullable=False,
        server_default=text("'BOT'::character varying"), comment='目标类型')
    target_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='目标uid')
    config_mode: Mapped[str] = mapped_column(String(32), nullable=False, comment='配置模式')
    config_content: Mapped[dict] = mapped_column(Dict2Json, nullable=False, comment='配置内容')
    publish_status: Mapped[PublishConfigStatus] = mapped_column(
        Enum(PublishConfigStatus, native_enum=False), nullable=False,
        server_default=text("'DRAFT'::character varying"), comment='发布状态')
