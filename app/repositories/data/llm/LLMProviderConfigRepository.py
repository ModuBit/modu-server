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
from repositories.data.llm.llm_models import LLMProviderConfig


class LLMProviderConfigRepository(Repository):
    """
    空间数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def add(
            self, llm_provider_config: LLMProviderConfig, session: AsyncSession) -> LLMProviderConfig:
        """
        新增Provider配置
        :param llm_provider_config: llm provider
        :param session: Session
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
            self, llm_provider_config: LLMProviderConfig, session: AsyncSession) -> LLMProviderConfig:
        """
        修改Provider配置
        :param llm_provider_config: llm provider
        :param session: Session
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(
            self, workspace_uid: str, provider_key: str, session: AsyncSession) -> bool:
        """
        删除Provider配置
        :param workspace_uid: workspace uid
        :param provider_key: provider key
        :param session: Session
        """
        raise NotImplementedError

    @abstractmethod
    async def find_one_by_workspace_and_key(
            self, workspace_uid: str, provider_key: str, session: AsyncSession) -> LLMProviderConfig | None:
        """
        根据workspace uid和provider key查询配置
        :param workspace_uid: workspace uid
        :param provider_key: provider key
        :param session: Session
        """
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, workspace_uid: str, session: AsyncSession) -> list[LLMProviderConfig]:
        """
        列出所有配置
        :param workspace_uid: workspace uid
        :param session: Session
        """
        raise NotImplementedError
