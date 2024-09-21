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

from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.database import BasePO, with_async_session, AliasMapper
from repositories.data.message.ConversationRepository import ConversationRepository
from repositories.data.message.conversation_models import Conversation
from repositories.data.postgres_database import PostgresBasePO
from utils.dictionary import dict_exclude_keys

_alias_mapping: Dict[str, AliasMapper] = {
    'uid': AliasMapper(alias='conversation_uid')
}


class ConversationRepositoryPostgres(ConversationRepository):
    """
    会话数据存储的Postgres实现
    """

    @with_async_session
    async def get_by_uid(self, creator_uid: str, conversation_uid: str, session: AsyncSession) -> Conversation:
        stmt = (select(ConversationPO)
                .where(ConversationPO.creator_uid == creator_uid)
                .where(ConversationPO.uid == conversation_uid)
                .where(ConversationPO.is_deleted == False)
                .limit(1))
        select_result = await session.execute(stmt)
        conversation_model = select_result.scalars().one_or_none()
        return Conversation(**conversation_model.as_dict(alias_mapping=_alias_mapping)) if conversation_model else None

    @with_async_session
    async def create(self, conversation: Conversation, session: AsyncSession) -> Conversation:
        conversation_po = ConversationPO(**dict_exclude_keys(vars(conversation), ['conversation_uid']))
        conversation_po.uid = BasePO.uid_generate()
        session.add(conversation_po)
        conversation.conversation_uid = conversation_po.uid
        return conversation


class ConversationPO(PostgresBasePO):
    """
    会话PO
    """

    __tablename__ = 'modu_conversations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    creator_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='创建者uid')
    workspace_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='空间uid')
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment='会话名')
    reset_message_uid: Mapped[str] = mapped_column(String(32), nullable=True, comment='重置/清楚记忆 时的消息UID')
