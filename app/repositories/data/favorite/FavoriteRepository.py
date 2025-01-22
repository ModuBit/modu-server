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
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.data.favorite.favorite_models import FavoriteTargetType
from repositories.data.database import Database, Repository


class FavoriteRepository(Repository):
    """
    收藏数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def favorite(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uid: str,
        session: AsyncSession,
    ) -> True:
        """
        收藏
        :param creator_uid: 收藏者uid
        :param target_type: 目标类型
        :param target_uid: 目标uid
        :param session: 数据库会话
        :return: True / False
        """
        raise NotImplementedError()

    @abstractmethod
    async def un_favorite(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uid: str,
        session: AsyncSession,
    ) -> bool:
        """
        取消收藏
        :param creator_uid: 收藏者uid
        :param target_type: 目标类型
        :param target_uid: 目标uid
        :param session: 数据库会话
        :return: True / False
        """
        raise NotImplementedError()

    @abstractmethod
    async def is_favorite(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uid: str,
        session: AsyncSession,
    ) -> bool:
        """
        是否收藏
        :param creator_uid: 收藏者uid
        :param target_type: 目标类型
        :param target_uid: 目标uid
        :param session: 数据库会话
        :return: 目标uid列表和是否收藏的映射
        """
        raise NotImplementedError()

    @abstractmethod
    async def is_favorites(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uids: List[str],
        session: AsyncSession,
    ) -> dict[str, bool]:
        """
        是否收藏
        :param creator_uid: 收藏者uid
        :param target_type: 目标类型
        :param target_uids: 目标uid列表
        :param session: 数据库会话
        :return: 目标uid列表和是否收藏的映射
        """
        raise NotImplementedError()
