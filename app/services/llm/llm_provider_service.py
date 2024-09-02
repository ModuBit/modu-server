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
from repositories.cache import cache_decorator_builder
from repositories.cache.cache import CacheDecorator
from repositories.data import llm_provider_config_repository
from repositories.data.account.account_models import Account
from repositories.data.llm.llm_models import LLMProviderConfig
from repositories.data.workspace.workspace_models import WorkspaceMemberRole
from services import workspace_service
from utils.constants import HIDDEN_PREFIX
from utils.desensitize import desensitize
from utils.errors.base_error import UnauthorizedError
from utils.errors.llm_error import LLMExistsError

# noinspection DuplicatedCode
llm_provider_config_cache: CacheDecorator[LLMProviderConfig] = cache_decorator_builder.build(
    serialize=lambda provider_config: provider_config.copy().encrypt_credential().model_dump_json(),
    deserialize=lambda json_content: LLMProviderConfig.parse_raw(json_content).decrypt_credential(),
    default_expire_seconds=24 * 3600,
    allow_none_values=True,
)

llm_provider_configured_config_cache: CacheDecorator[list[LLMProviderConfig]] = cache_decorator_builder.build(
    serialize=lambda provider_configs: json.dumps([provider_config.copy().encrypt_credential().dict()
                                                   for provider_config in provider_configs]),
    deserialize=lambda json_contents: [LLMProviderConfig.parse_obj(json_obj).decrypt_credential()
                                       for json_obj in json.loads(json_contents)],
    default_expire_seconds=24 * 3600,
    allow_none_values=True,
)


async def add(current_user: Account, workspace_uid: str, provider_name: str,
              provider_config: LLMProviderConfig) -> LLMProviderConfig:
    """
    添加LLM Provider配置
    :param current_user: 当前用户
    :param workspace_uid: 工作空间UID
    :param provider_name: Provider Name
    :param provider_config: Provider配置
    :return: LLMProviderConfig
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None or member_role not in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]:
        raise UnauthorizedError('您无该权限操作')

    return await _add(workspace_uid, provider_name, provider_config)


@llm_provider_config_cache.async_cache_put(
    key_generator=lambda workspace_uid, provider_name, **kwargs:
    f"workspace:{workspace_uid}:llm:provider:{provider_name}:config")
@llm_provider_configured_config_cache.async_cache_evict(
    key_generator=lambda workspace_uid, **kwargs: f"workspace:{workspace_uid}:llm:provider:configured:config")
async def _add(workspace_uid: str, provider_name: str,
               provider_config: LLMProviderConfig) -> LLMProviderConfig:
    """
    添加LLM Provider配置
    :param workspace_uid: 工作空间UID
    :param provider_name: Provider Name
    :param provider_config: Provider配置
    :return: LLMProviderConfig
    """
    llm_provider = model_provider_factory.get_provider(provider_name)
    if llm_provider is None:
        raise LLMExistsError('LLM供应商不存在')

    exists_provider_config = await llm_provider_config_repository.find_one_by_workspace_and_provider_name(workspace_uid,
                                                                                                          provider_name)

    # 处理脱敏字段值
    exists_credential = exists_provider_config.provider_credential if exists_provider_config else {}
    adding_credential = provider_config.provider_credential or {}
    for key, value in adding_credential.items():
        # 如果携带HIDDEN_PREFIX，说明未对该值进行修改
        if isinstance(value, str) and value.startswith(HIDDEN_PREFIX):
            adding_credential[key] = exists_credential[key]

    # 凭证验证
    await llm_provider.validate_credentials(adding_credential)

    return await llm_provider_config_repository.add(provider_config) if exists_provider_config is None \
        else await llm_provider_config_repository.update(provider_config)


@llm_provider_config_cache.async_cache_evict(
    key_generator=lambda workspace_uid, provider_name, **kwargs:
    f"workspace:{workspace_uid}:llm:provider:{provider_name}:config")
@llm_provider_configured_config_cache.async_cache_evict(
    key_generator=lambda workspace_uid, **kwargs: f"workspace:{workspace_uid}:llm:provider:configured:config")
async def delete(current_user: Account, workspace_uid: str, provider_name: str) -> bool:
    """
    删除 LLM Provider 配置
    :param current_user: 当前用户
    :param workspace_uid: 工作空间 UID
    :param provider_name: LLM 提供商 key
    :return: True False
    """
    llm_provider = model_provider_factory.get_provider(provider_name)
    if llm_provider is None:
        raise LLMExistsError('LLM供应商不存在')

    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None or member_role not in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]:
        raise UnauthorizedError('您无该权限操作')

    return await llm_provider_config_repository.delete(workspace_uid, provider_name)


async def detail(current_user: Account, workspace_uid: str, provider_name: str) -> LLMProviderConfig:
    """
    获取 LLM Provider配置
    :param current_user: 当前用户
    :param workspace_uid: 工作空间 UID
    :param provider_name: LLM 提供商 key
    :return: LLM Provider 配置
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该权限查看')

    return await _detail(workspace_uid, provider_name)


@llm_provider_config_cache.async_cacheable(
    key_generator=lambda workspace_uid, provider_name, **kwargs:
    f"workspace:{workspace_uid}:llm:provider:{provider_name}:config")
async def _detail(workspace_uid: str, provider_name: str) -> LLMProviderConfig:
    """
    获取 LLM Provider配置
    :param workspace_uid: 工作空间 UID
    :param provider_name: LLM 提供商 key
    :return: LLM Provider 配置
    """
    return await llm_provider_config_repository.find_one_by_workspace_and_provider_name(workspace_uid, provider_name)


async def all_configured(current_user: Account, workspace_uid: str) -> list[LLMProviderConfig]:
    """
    获取所有已配置的 Provider
    :param current_user: 当前用户
    :param workspace_uid: 工作空间 UID
    :return: LLMProviderConfig
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该权限查看')

    return await _all_configured(workspace_uid)


@llm_provider_configured_config_cache.async_cacheable(
    key_generator=lambda workspace_uid, **kwargs: f"workspace:{workspace_uid}:llm:provider:configured:config")
async def _all_configured(workspace_uid: str) -> list[LLMProviderConfig]:
    """
    获取所有已配置的 Provider
    :param workspace_uid: 工作空间 UID
    :return: LLMProviderConfig
    """
    return await llm_provider_config_repository.list_all(workspace_uid)


def provider_config_desensitize(provider_config: LLMProviderConfig | None) -> LLMProviderConfig | None:
    """
    LLM Provider脱敏
    :param provider_config: LLMProviderConfig
    :return: LLMProviderConfig
    """

    if provider_config is None:
        return None

    llm_provider = model_provider_factory.get_provider(provider_config.provider_name)

    # 在凭证数据中找出所有password类型的字段
    credential_schemas = llm_provider.provider_schema.credential_schemas
    sensitized_keys = [credential_schema.name for credential_schema in credential_schemas
                       if credential_schema.value_type == 'password']

    # 将凭证数据中password类型的字段进行脱敏
    for (key, value) in provider_config.provider_credential.items():
        if key not in sensitized_keys:
            continue
        if value.startswith(HIDDEN_PREFIX):
            continue
        provider_config.provider_credential[key] = desensitize(value, HIDDEN_PREFIX)

    return provider_config
