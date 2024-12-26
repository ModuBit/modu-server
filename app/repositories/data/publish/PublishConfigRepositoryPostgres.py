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

from sqlalchemy import (
    TypeDecorator,
    PrimaryKeyConstraint,
    String,
    text,
    Enum,
    update,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from repositories.data.database import with_async_session, BasePO
from repositories.data.postgres_database import PostgresBasePO
from repositories.data.publish.PublishConfigRepository import PublishConfigRepository
from repositories.data.publish.publish_config import (
    PublishConfigTargetType,
    PublishConfigStatus,
    PublishConfig,
)


class PublishConfigRepositoryPostgres(PublishConfigRepository):
    """
    发布配置数据存储的PostgreSQL实现
    """

    @with_async_session
    async def get_draft(
        self, target_type: str, target_uid: str, session: AsyncSession
    ) -> PublishConfig:
        stmt = (
            select(PublishConfigPO)
            .where(PublishConfigPO.target_type == target_type)
            .where(PublishConfigPO.target_uid == target_uid)
            .where(PublishConfigPO.publish_status == PublishConfigStatus.DRAFT)
            .where(PublishConfigPO.is_deleted == False)
        )
        select_result = await session.execute(stmt)
        bot_model = select_result.scalars().one_or_none()
        return PublishConfig(**bot_model.as_dict()) if bot_model else None

    @with_async_session
    async def get_version(
        self, target_type: str, target_uid: str, version_uid: str, session: AsyncSession
    ) -> PublishConfig:
        stmt = (
            select(PublishConfigPO)
            .where(PublishConfigPO.target_type == target_type)
            .where(PublishConfigPO.target_uid == target_uid)
            .where(PublishConfigPO.uid == version_uid)
            .where(PublishConfigPO.is_deleted == False)
        )
        select_result = await session.execute(stmt)
        bot_model = select_result.scalars().one_or_none()
        return PublishConfig(**bot_model.as_dict()) if bot_model else None

    @with_async_session
    async def draft_exists(
        self, target_type: str, target_uid: str, session: AsyncSession
    ) -> str:
        stmt = (
            select(PublishConfigPO.uid)
            .where(PublishConfigPO.target_type == target_type)
            .where(PublishConfigPO.target_uid == target_uid)
            .where(PublishConfigPO.publish_status == PublishConfigStatus.DRAFT)
            .where(PublishConfigPO.is_deleted == False)
        )
        select_result = await session.execute(stmt)
        publish_uid = select_result.scalars().one_or_none()
        return publish_uid

    @with_async_session
    async def save_or_update(
        self,
        publish_config: PublishConfig,
        publish_status: PublishConfigStatus,
        session: AsyncSession,
    ) -> PublishConfig:
        draft_uid = await self.draft_exists(
            publish_config.target_type, publish_config.target_uid, session
        )
        if draft_uid:
            stmt = (
                update(PublishConfigPO)
                .where(PublishConfigPO.target_type == publish_config.target_type)
                .where(PublishConfigPO.target_uid == publish_config.target_uid)
                .values(
                    config_mode=publish_config.config_mode,
                    config_content=publish_config.config_content,
                    publish_status=publish_status,
                )
            )
            await session.execute(stmt)
            publish_config.uid = draft_uid
        else:
            publish_po = PublishConfigPO(**vars(publish_config))
            publish_po.publish_status = publish_status
            publish_po.uid = BasePO.uid_generate()
            session.add(publish_po)
            publish_config.uid = publish_po.uid
        return publish_config


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

    __tablename__ = "modu_publish_configs"
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_id"),)

    target_type: Mapped[PublishConfigTargetType] = mapped_column(
        Enum(PublishConfigTargetType, native_enum=False),
        nullable=False,
        server_default=text("'BOT'::character varying"),
        comment="目标类型",
    )
    target_uid: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="目标uid"
    )
    config_mode: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="配置模式"
    )
    config_content: Mapped[dict] = mapped_column(
        Dict2Json, nullable=False, comment="配置内容"
    )
    publish_status: Mapped[PublishConfigStatus] = mapped_column(
        Enum(PublishConfigStatus, native_enum=False),
        nullable=False,
        server_default=text("'DRAFT'::character varying"),
        comment="发布状态",
    )
