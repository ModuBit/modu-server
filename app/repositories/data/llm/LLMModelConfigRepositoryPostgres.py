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

from sqlalchemy import TypeDecorator, PrimaryKeyConstraint, String, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from llm.model.entities.model import ModelType
from repositories.data.database import with_async_session
from repositories.data.postgres_database import PostgresBasePO
from repositories.data.llm import LLMModelConfigRepository
from repositories.data.llm.llm_models import LLMModelConfig


class LLMModelConfigRepositoryPostgres(LLMModelConfigRepository):
    """
    LLM Model 配置数据存储的PostgreSQL实现
    """

    @with_async_session
    async def add_system_models(
        self,
        workspace_uid: str,
        llm_model_configs: dict[ModelType, LLMModelConfig],
        session: AsyncSession,
    ) -> dict[ModelType, LLMModelConfig]:
        llm_system_model_config_po = LLMSystemModelConfigPO(
            workspace_uid=workspace_uid, model_config=llm_model_configs
        )
        session.add(llm_system_model_config_po)
        return llm_model_configs

    @with_async_session
    async def update_system_models(
        self,
        workspace_uid: str,
        llm_model_configs: dict[ModelType, LLMModelConfig],
        session: AsyncSession,
    ) -> dict[ModelType, LLMModelConfig]:
        stmt = (
            update(LLMSystemModelConfigPO)
            .where(LLMSystemModelConfigPO.workspace_uid == workspace_uid)
            .values(model_config=llm_model_configs)
        )
        await session.execute(stmt)

        return llm_model_configs

    @with_async_session
    async def find_system_models_by_workspace(
        self, workspace_uid: str, session: AsyncSession
    ) -> dict[ModelType, LLMModelConfig] | None:
        stmt = (
            select(LLMSystemModelConfigPO)
            .where(LLMSystemModelConfigPO.workspace_uid == workspace_uid)
            .where(LLMSystemModelConfigPO.is_deleted == False)
            .limit(1)
        )
        select_result = await session.execute(stmt)
        system_model = select_result.scalars().one_or_none()
        if system_model is None:
            return None

        return system_model.model_config


class LLMModelConfigDict2Json(TypeDecorator):
    """
    dict[ModelType, LLMModelConfig] 和 dict[string, dict] 互转，用于JSONB存储
    """

    impl = JSONB

    cache_ok = False

    def process_bind_param(self, value, dialect):
        """
        Convert dict[ModelType, LLMModelConfig] to dict[string, dict]
        """
        if value is not None:
            value = {
                model_type.value: model_config.model_dump()
                for model_type, model_config in value.items()
            }
        return value

    def process_result_value(self, value, dialect):
        """
        Convert dict[string, dict] to dict[ModelType, LLMModelConfig]
        """
        if value is not None:
            value = {
                ModelType(model_type.upper()): LLMModelConfig.model_validate(
                    model_config
                )
                for model_type, model_config in value.items()
            }
        return value


class LLMSystemModelConfigPO(PostgresBasePO):
    """
    LLM 系统默认模型配置
    """

    __tablename__ = "modu_llm_system_model_config"
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_id"),)

    workspace_uid: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="provider配置uid"
    )
    model_config: Mapped[dict[ModelType, LLMModelConfig]] = mapped_column(
        LLMModelConfigDict2Json, nullable=False, comment="系统默认模型配置"
    )
