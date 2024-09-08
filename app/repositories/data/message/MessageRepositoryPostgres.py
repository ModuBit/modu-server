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

from sqlalchemy import PrimaryKeyConstraint, String, BIGINT, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.database import with_async_session, BasePO, AliasMapper
from repositories.data.message.ConversationRepositoryPostgres import ConversationPO
from repositories.data.message.MessageRepository import MessageRepository
from repositories.data.message.message_models import MessageBlock, Message
from repositories.data.postgres_database import PostgresBasePO
from utils.dictionary import dict_exclude_keys
from utils.json import default_excluded_fields

_alias_mapping: Dict[str, AliasMapper] = {
    'uid': AliasMapper(alias='message_uid')
}


class MessageRepositoryPostgres(MessageRepository):
    """
    会话消息数据存储的Postgres实现
    """

    @staticmethod
    def _convert(message: Message):
        message_po = MessagePO(**dict_exclude_keys(vars(message), ['message_uid']))
        if message.message_uid:
            message_po.uid = message.message_uid
        else:
            message_po.uid = BasePO.uid_generate()
            message.message_uid = message_po.uid
        return message_po

    @with_async_session
    async def add(self, message: Message, session: AsyncSession) -> Message:
        message_po = MessageRepositoryPostgres._convert(message)
        session.add(message_po)
        return message

    @with_async_session
    async def add_batch(self, messages: list[Message], session: AsyncSession) -> list[Message]:
        message_pos = [MessageRepositoryPostgres._convert(message) for message in messages]
        session.add_all(message_pos)
        return messages

    @with_async_session
    async def find_latest(self, creator_uid: str, conversation_uid: str, latest_count: int,
                          session: AsyncSession) -> list[Message]:
        stmt = (select(Message)
                .join(ConversationPO, ConversationPO.uid == MessagePO.conversation_uid)
                .where(MessagePO.conversation_uid == conversation_uid)
                .where(ConversationPO.creator_uid == creator_uid)
                .order_by(MessagePO.message_time.desc())
                .limit(latest_count))
        select_result = await session.execute(stmt)
        return [Message(**message.as_dict(alias_mapping=_alias_mapping)) for message in select_result.scalars()]

    @with_async_session
    async def find_all_after_time(self, creator_uid: str, conversation_uid: str, after_time: int,
                                  session: AsyncSession) -> list[Message]:
        stmt = (select(Message)
                .join(ConversationPO, ConversationPO.uid == MessagePO.conversation_uid)
                .where(MessagePO.conversation_uid == conversation_uid)
                .where(MessagePO.message_time > after_time)
                .where(ConversationPO.creator_uid == creator_uid)
                .order_by(MessagePO.message_time.desc()))
        select_result = await session.execute(stmt)
        return [Message(**message.as_dict(alias_mapping=_alias_mapping)) for message in select_result.scalars()]


class MessageBlocks2Jsonb(TypeDecorator):
    impl = JSONB

    def process_bind_param(self, value, dialect):
        """
        Convert Python list[MessageContent] to database jsonb
        """
        if value is not None:
            value = [message_block.model_dump(exclude=default_excluded_fields) for message_block in value]
        return value

    def process_result_value(self, value, dialect):
        """
        Convert database jsonb to Python list[MessageContent]
        """
        if value is not None:
            value = [MessageBlock.model_validate_json(json_obj) for json_obj in value],
        return value


class MessagePO(PostgresBasePO):
    """
    消息PO
    """

    __tablename__ = 'modu_messages'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    conversation_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='会话uid')
    message_time: Mapped[int] = mapped_column(BIGINT(), nullable=False, comment='消息时间戳')
    sender_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='发送者uid')
    sender_role: Mapped[str] = mapped_column(String(32), nullable=False, comment='发送者角色')
    messages: Mapped[list[MessageBlock]] = mapped_column(MessageBlocks2Jsonb(), nullable=False, comment='消息')
