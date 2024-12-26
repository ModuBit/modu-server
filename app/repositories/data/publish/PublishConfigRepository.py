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
from repositories.data.publish.publish_config import PublishConfig, PublishConfigStatus


class PublishConfigRepository(Repository):
    """
    配置发布数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def get_draft(
        self, target_type: str, target_uid: str, session: AsyncSession
    ) -> PublishConfig:
        """
        获取草稿数据
        :param target_type: 目标类型
        :param target_uid: 目标 UID
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_version(
        self, target_type: str, target_uid: str, version_uid: str, session: AsyncSession
    ) -> PublishConfig:
        """
        获取特定版本数据
        :param target_type: 目标类型
        :param target_uid: 目标 UID
        :param version_uid: 版本 UID
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def draft_exists(
        self, target_type: str, target_uid: str, session: AsyncSession
    ) -> bool:
        """
        判断是否存在草稿
        :param target_type: 目标类型
        :param target_uid: 目标 UID
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def save_or_update(
        self,
        publish_config: PublishConfig,
        publish_status: PublishConfigStatus,
        session: AsyncSession,
    ) -> PublishConfig:
        """
        保存/更新
        :param publish_config:
        :param publish_status:
        :param session:
        :return:
        """
        raise NotImplementedError()
