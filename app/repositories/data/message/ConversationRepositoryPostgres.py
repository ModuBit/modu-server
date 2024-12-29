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

from typing import Dict

from sqlalchemy import PrimaryKeyConstraint, String, text, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.database import BasePO, with_async_session, AliasMapper
from repositories.data.message.ConversationRepository import ConversationRepository
from repositories.data.message.conversation_models import Conversation
from repositories.data.postgres_database import PostgresBasePO
from utils.dictionary import dict_exclude_keys

_alias_mapping: Dict[str, AliasMapper] = {
    "uid": AliasMapper(alias="conversation_uid"),
    "created_at": AliasMapper(
        alias="created_at", value=lambda created_at: created_at.timestamp() * 1000
    ),
}


class ConversationRepositoryPostgres(ConversationRepository):
    """
    会话数据存储的Postgres实现
    """

    @with_async_session
    async def get_by_uid(
        self, creator_uid: str, conversation_uid: str, session: AsyncSession
    ) -> Conversation:
        stmt = (
            select(ConversationPO)
            .where(ConversationPO.creator_uid == creator_uid)
            .where(ConversationPO.uid == conversation_uid)
            .where(ConversationPO.is_deleted == False)
            .limit(1)
        )
        select_result = await session.execute(stmt)
        conversation_model = select_result.scalars().one_or_none()
        return (
            Conversation(**conversation_model.as_dict(alias_mapping=_alias_mapping))
            if conversation_model
            else None
        )

    @with_async_session
    async def find_before_uid(
        self,
        scope: str | None,
        creator_uid: str,
        before_uid: str | None,
        include_this: bool,
        max_count: int,
        session: AsyncSession,
    ) -> list[Conversation]:
        stmt = (
            select(ConversationPO)
            .where(ConversationPO.scope == (scope or ConversationRepository.SCOPE_ALL))
            .where(ConversationPO.creator_uid == creator_uid)
            .where(ConversationPO.is_deleted == False)
        )

        if before_uid:
            before_uid_subquery = (
                select(ConversationPO.created_at)
                .where(ConversationPO.uid == before_uid)
                .where(ConversationPO.is_deleted == False)
            ).scalar_subquery()
            stmt = (
                stmt.where(ConversationPO.created_at <= before_uid_subquery)
                if include_this
                else stmt.where(ConversationPO.created_at < before_uid_subquery)
            )

        stmt = stmt.order_by(ConversationPO.created_at.desc()).limit(max_count)
        select_result = await session.execute(stmt)
        return [
            Conversation(**conv.as_dict(alias_mapping=_alias_mapping))
            for conv in select_result.scalars()
        ]

    @with_async_session
    async def create(
        self, conversation: Conversation, session: AsyncSession
    ) -> Conversation:
        conversation_po = ConversationPO(
            **dict_exclude_keys(vars(conversation), ["conversation_uid", "create_at"])
        )
        conversation_po.uid = BasePO.uid_generate()
        session.add(conversation_po)
        conversation.conversation_uid = conversation_po.uid
        return conversation

    @with_async_session
    async def update_reset_message_uid(
        self, conversation_uid: str, reset_message_uid: str, session: AsyncSession
    ):
        stmt = (
            update(ConversationPO)
            .where(ConversationPO.uid == conversation_uid)
            .values(reset_message_uid=reset_message_uid)
        )
        await session.execute(stmt)

        return reset_message_uid

    @with_async_session
    async def delete_by_uid(self, conversation_uid: str, session: AsyncSession) -> bool:
        stmt = (
            update(ConversationPO)
            .where(ConversationPO.uid == conversation_uid)
            .values(is_deleted=True)
        )
        await session.execute(stmt)
        return True

    @with_async_session
    async def delete_all_by_creator(
        self, creator_uid: str, session: AsyncSession
    ) -> bool:
        stmt = (
            update(ConversationPO)
            .where(ConversationPO.creator_uid == creator_uid)
            .values(is_deleted=True)
        )
        await session.execute(stmt)
        return True

    @with_async_session
    async def update_name(
        self, conversation_uid: str, name: str, session: AsyncSession
    ) -> str:
        stmt = (
            update(ConversationPO)
            .where(ConversationPO.uid == conversation_uid)
            .values(name=name)
        )
        await session.execute(stmt)
        return name


class ConversationPO(PostgresBasePO):
    """
    会话PO
    """

    __tablename__ = "modu_conversations"
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_id"),)

    creator_uid: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="创建者uid"
    )
    workspace_uid: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="空间uid"
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="会话名")
    reset_message_uid: Mapped[str] = mapped_column(
        String(32), nullable=True, comment="重置/清除记忆 时的消息UID"
    )
    scope: Mapped[str] = mapped_column(
        String(32),
        nullable=True,
        server_default=text("'ALL'::character varying"),
        comment="范围",
    )
