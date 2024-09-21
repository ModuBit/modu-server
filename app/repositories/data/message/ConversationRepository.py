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
from abc import abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.data.database import Repository, Database
from repositories.data.message.conversation_models import Conversation


class ConversationRepository(Repository):
    """
    会话数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def get_by_uid(self, creator_uid: str, conversation_uid: str, session: AsyncSession) -> Conversation:
        """
        通过uid查询会话
        :param creator_uid: 用户 uid
        :param conversation_uid: 会话uid
        :return Conversation
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def create(self, conversation: Conversation, session: AsyncSession) -> Conversation:
        """
        创建会话
        :param conversation: 会话
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def update_reset_message_uid(self, conversation_uid: str, reset_message_uid: str,
                                       session: AsyncSession) -> str:
        """
        更新 重置/清楚记忆 时的消息UID
        :param conversation_uid: 会话UID
        :param reset_message_uid: 重置/清楚记忆 时的消息UID
        :param session: Session
        """
        raise NotImplementedError()
