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

from llm.model import model_provider_factory
from llm.model.entities.model import ModelType, ModelSchema
from llm.model.entities.provider import ProviderWithModelsSchema, ProviderStatus
from repositories.data import llm_provider_config_repository
from repositories.data.account.account_models import Account
from services import workspace_service
from utils.errors.base_error import UnauthorizedError
from utils.errors.llm_error import LLMExistsError


async def get_models(current_user: Account,
                     workspace_uid: str,
                     provider_name: str | None = None,
                     model_type: ModelType | None = None,
                     only_active: bool = False) -> list[ProviderWithModelsSchema]:
    """
    获取空间下的模型
    可以指定 只获取某一Provider的模型
    可以指定 只获取某一类型的模型
    可以指定 只获取可使用的模型
    :param current_user: 当前用户
    :param workspace_uid: 工作空间UID
    :param provider_name: Provider Name 缺省获取所有Provider
    :param model_type: 模型类型 缺省获取所有类型模型
    :param only_active: 是否只获取激活的模型
    :return: ProviderWithModelsSchema
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该权限查看')

    provider_with_models: list[ProviderWithModelsSchema] = []

    # 获取Providers
    # 如果指定provider_name，则获取对应的Provider
    llm_providers = [model_provider_factory.get_provider(provider_name)] if provider_name \
        else model_provider_factory.providers
    llm_providers = filter(lambda p: p.provider, llm_providers)
    if not llm_providers:
        raise LLMExistsError('LLM供应商不存在')

    # 所有已配置的Provider信息
    configured_providers = await llm_provider_config_repository.list_all(workspace_uid)
    configured_provider_names = set(map(lambda p: p.provider_name, configured_providers))

    # 如果指定only_active，则获取已配置的Providers
    if only_active:
        llm_providers = filter(lambda p: p.provider in configured_provider_names, llm_providers)
    if not llm_providers:
        return provider_with_models

    for llm_provider in llm_providers:
        models: list[ModelSchema] = []

        # 如果指定model_type，则获取对应类型的模型

        # 来自 系统预配置
        for model in llm_provider.get_models(model_type):
            models.extend(model.model_schemas)

        # TODO 来自 用户自定义

        provider_with_models.append(ProviderWithModelsSchema(
            provider=llm_provider.provider_schema,
            models=models,
            status=ProviderStatus.ACTIVE if llm_provider.provider in configured_provider_names
            else ProviderStatus.UN_CONFIGURED
        ))

    return provider_with_models
