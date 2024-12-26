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

from llm.model.entities.model import ModelType
from repositories.data.database import Repository, Database
from repositories.data.llm.llm_models import LLMModelConfig


class LLMModelConfigRepository(Repository):
    """
    LLM 模型 配置数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def add_system_models(
        self,
        workspace_uid: str,
        llm_model_configs: dict[ModelType, LLMModelConfig],
        session: AsyncSession,
    ) -> dict[ModelType, LLMModelConfig]:
        """
        新增某空间系统模型配置
        :param workspace_uid: 空间UID
        :param llm_model_configs: 模型配置
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def update_system_models(
        self,
        workspace_uid: str,
        llm_model_configs: dict[ModelType, LLMModelConfig],
        session: AsyncSession,
    ) -> dict[ModelType, LLMModelConfig]:
        """
        修改某空间系统模型配置
        :param workspace_uid: 空间UID
        :param llm_model_configs: 模型配置
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def find_system_models_by_workspace(
        self, workspace_uid: str, session: AsyncSession
    ) -> dict[ModelType, LLMModelConfig]:
        """
        获取某空间系统模型配置
        :param workspace_uid: 空间UID
        :param session: Session
        """
        raise NotImplementedError()
