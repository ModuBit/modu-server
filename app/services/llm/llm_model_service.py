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

import json

from llm.model import model_provider_factory
from llm.model.entities.model import ModelType, ModelSchema
from llm.model.entities.provider import ProviderWithModelsSchema, ProviderStatus
from repositories.cache import cache_decorator_builder
from repositories.cache.cache import CacheDecorator
from repositories.data import llm_model_config_repository
from repositories.data.account.account_models import Account
from repositories.data.llm.llm_models import LLMModelConfig
from services import workspace_service
from utils.dictionary import dict_get
from utils.errors.base_error import UnauthorizedError
from utils.errors.llm_error import LLMExistsError
from . import llm_provider_service

llm_system_model_config_cache: CacheDecorator[dict[ModelType, LLMModelConfig]] = cache_decorator_builder.build(
    # Convert dict[ModelType, LLMModelConfig] to dict[string, dict]
    serialize=lambda system_model_config: json.dumps({model_type.value: model_config.dict()
                                                      for model_type, model_config in system_model_config.items()}),
    # Convert dict[string, dict] to dict[ModelType, LLMModelConfig]
    deserialize=lambda json_content: {ModelType(model_type.upper()): LLMModelConfig.parse_obj(model_config)
                                      for model_type, model_config in json.loads(json_content).items()},
    default_expire_seconds=24 * 3600,
    allow_none_values=True,
)


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

    return await _get_models(workspace_uid, provider_name, model_type, only_active)


# noinspection PyProtectedMember
async def _get_models(workspace_uid: str,
                      provider_name: str | None = None,
                      model_type: ModelType | None = None,
                      only_active: bool = False) -> list[ProviderWithModelsSchema]:
    """
    获取空间下的模型
    可以指定 只获取某一Provider的模型
    可以指定 只获取某一类型的模型
    可以指定 只获取可使用的模型
    :param workspace_uid: 工作空间UID
    :param provider_name: Provider Name 缺省获取所有Provider
    :param model_type: 模型类型 缺省获取所有类型模型
    :param only_active: 是否只获取激活的模型
    :return: ProviderWithModelsSchema
    """
    provider_with_models: list[ProviderWithModelsSchema] = []

    # 获取Providers
    # 如果指定provider_name，则获取对应的Provider
    llm_providers = [model_provider_factory.get_provider(provider_name)] if provider_name \
        else model_provider_factory.providers
    llm_providers = filter(lambda p: p.provider, llm_providers)
    if not llm_providers:
        raise LLMExistsError('LLM供应商不存在')

    # 所有已配置的Provider信息
    configured_providers = await llm_provider_service._all_configured(workspace_uid)
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


async def check_and_renew_llm_model_config(workspace_uid: str, model_type: ModelType,
                                           model_config: LLMModelConfig) -> LLMModelConfig:
    """
    校验参数，并过滤有效参数
    :param workspace_uid: 工作空间UID
    :param model_type: 模型类型
    :param model_config: 模型配置
    :return: LLMModelConfig
    """
    provider_with_models_schemas = await _get_models(workspace_uid, model_config.provider_name, model_type)
    if not provider_with_models_schemas:
        raise LLMExistsError('LLM供应商不存在')

    provider_with_models_schema: ProviderWithModelsSchema = next(
        filter(lambda s: s.provider.provider == model_config.provider_name, provider_with_models_schemas), None)
    if not provider_with_models_schema:
        raise LLMExistsError('LLM供应商不存在')

    model_schema = next(
        filter(lambda m: m.model == model_config.model_name, provider_with_models_schema.models), None)
    if not model_schema:
        raise LLMExistsError('LLM模型不存在')

    return _check_and_renew_llm_model_config(model_config, model_schema)


def _check_and_renew_llm_model_config(model_config: LLMModelConfig, model_schema: ModelSchema) -> LLMModelConfig:
    """
    校验参数，并过滤有效参数
    :param model_config: 模型配置
    :param model_schema: 模型Schema
    :return: LLMModelConfig
    """
    # 配置中的参数
    model_parameters = model_config.model_parameters or {}
    # schema中的参数
    schema_parameters = model_schema.parameters or {}

    # 只取有效的参数
    valid_parameters = {key: value for key, value in model_parameters.items()
                        if any(param.name == key for param in schema_parameters)}

    # 校验必须参数
    for schema_parameter in [schema_parameter for schema_parameter in schema_parameters if
                             schema_parameter.rules and schema_parameter.rules.required]:
        if schema_parameter.name not in valid_parameters or not valid_parameters[schema_parameter.name]:
            raise LLMExistsError(f'LLM模型{model_config.provider_name}:{model_config.model_name}'
                                 f'参数{schema_parameter.name}为必填项')

    # 校验数字范围
    for schema_parameter in [schema_parameter for schema_parameter in schema_parameters if
                             schema_parameter.value_type == 'digit' and schema_parameter.name in valid_parameters]:
        schema_min = dict_get(schema_parameter.field_props, 'min', None)
        if schema_min is not None and valid_parameters[schema_parameter.name] < schema_min:
            raise LLMExistsError(f'LLM模型{model_config.provider_name}:{model_config.model_name}'
                                 f'参数{schema_parameter.name}最小值不能小于{schema_min}')

        schema_max = dict_get(schema_parameter.field_props, 'max', None)
        if schema_max is not None and valid_parameters[schema_parameter.name] > schema_max:
            raise LLMExistsError(f'LLM模型{model_config.provider_name}:{model_config.model_name}'
                                 f'参数{schema_parameter.name}最大值不能大于{schema_max}')

    return LLMModelConfig(
        provider_name=model_config.provider_name,
        model_name=model_config.model_name,
        model_parameters=valid_parameters
    )


async def add_system_config(current_user: Account, workspace_uid: str,
                            llm_model_config: dict[ModelType, LLMModelConfig]) -> dict[ModelType, LLMModelConfig]:
    """
    添加 工作空间 系统默认模型配置
    :param current_user: 当前用户
    :param workspace_uid: 空间UID
    :param llm_model_config:  LLM模型配置
    :return:
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该权限查看')

    return await _add_system_config(workspace_uid, llm_model_config)


@llm_system_model_config_cache.async_cache_put(
    key_generator=lambda workspace_uid, **kwargs: f"workspace:{workspace_uid}:llm:system:model:config")
async def _add_system_config(workspace_uid: str,
                             llm_model_config: dict[ModelType, LLMModelConfig]) -> dict[ModelType, LLMModelConfig]:
    """
    添加 工作空间 系统默认模型配置
    :param workspace_uid: 空间UID
    :param llm_model_config:  LLM模型配置
    :return:
    """
    # 参数校验
    model_configs = {model_type: await check_and_renew_llm_model_config(workspace_uid, model_type, model_config)
                     for model_type, model_config in llm_model_config.items()}

    exists_model_config = await llm_model_config_repository.find_system_models_by_workspace(workspace_uid)
    return await llm_model_config_repository.add_system_models(workspace_uid, model_configs) \
        if exists_model_config is None \
        else await llm_model_config_repository.update_system_models(workspace_uid, model_configs)


async def get_system_config(current_user: Account, workspace_uid: str) -> dict[ModelType, LLMModelConfig]:
    """
    获取 工作空间 系统默认模型配置
    :param current_user: 当前用户
    :param workspace_uid: 工作空间UID
    :return: dict[ModelType, LLMModelConfig]
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该权限查看')

    return await _get_system_config(workspace_uid)


@llm_system_model_config_cache.async_cacheable(
    key_generator=lambda workspace_uid, **kwargs: f"workspace:{workspace_uid}:llm:system:model:config")
async def _get_system_config(workspace_uid: str) -> dict[ModelType, LLMModelConfig]:
    """
    获取 工作空间 系统默认模型配置
    :param workspace_uid: 工作空间UID
    :return: dict[ModelType, LLMModelConfig]
    """
    return await llm_model_config_repository.find_system_models_by_workspace(workspace_uid) or {}
