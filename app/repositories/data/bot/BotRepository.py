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
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.data.account.account_models import AccountInfo
from utils.pydantic import default_model_config
from repositories.data.bot.bot_models import Bot, BotFavoriteDTO, BotMode
from repositories.data.database import Repository, Database


class BotListQry(BaseModel):
    """
    智能体列表查询条件
    """

    keyword: str | None = None
    """关键词"""
    mode: BotMode | None = None
    """模式"""
    is_published: bool | None = None
    """是否发布"""
    after_uid_limit: str | None = None
    """从该uid后查询"""
    max_count: int = 20
    """返回数量"""


class BotFavoriteListQry(BaseModel):
    """
    智能体收藏列表查询条件
    """

    keyword: str | None = None
    """关键词"""
    after_uid_limit: str | None = None
    """从该uid后查询"""
    max_count: int = 20
    """返回数量"""


class BotRepository(Repository):
    """
    Bot数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def create(self, bot: Bot, session: AsyncSession) -> Bot:
        """
        创建智能体
        :param bot: 智能体
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def update_base_info(self, bot: Bot, session: AsyncSession) -> Bot:
        """
        更新智能体
        :param bot: 智能体
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def update_bot_config(
        self,
        bot_uid: str,
        bot_mode: BotMode,
        bot_config: dict,
        publish_uid: str,
        session: AsyncSession,
    ):
        """
        更新智能体
        :param bot_uid: 智能体uid
        :param bot_mode: 智能体模式
        :param bot_config: 智能体配置
        :param publish_uid: 发布uid
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_by_workspace_and_uid(
        self, workspace_uid: str, bot_uid: str, session: AsyncSession
    ) -> Bot:
        """
        通过uid查询会话
        :param workspace_uid: 空间uid
        :param bot_uid: 机器人uid
        :param session: Session
        :return Conversation
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_by_uid(
        self, bot_uid: str, session: AsyncSession
    ) -> Bot:
        """
        通过uid查询会话
        :param bot_uid: 机器人uid
        :param session: Session
        :return Conversation
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete_by_uid(self, bot_uid: str, session: AsyncSession) -> bool:
        """
        通过uid查询会话
        :param bot_uid: 机器人uid
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def find(
        self, workspace_uid: str, qry: BotListQry, session: AsyncSession
    ) -> list[Bot]:
        """
        查找某智能体前的智能体列表
        :param workspace_uid: 空间ID
        :param qry: 查询条件
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def find_favorite(
        self, favoriter_uid: str, qry: BotFavoriteListQry, session: AsyncSession
    ) -> list[BotFavoriteDTO]:
        """
        查找收藏智能体列表
        :param favoriter_uid: 收藏者uid
        :param qry: 查询条件
        :param session: Session
        """
        raise NotImplementedError()
