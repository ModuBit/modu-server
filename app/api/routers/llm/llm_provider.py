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

from fastapi import APIRouter, Depends
from loguru import logger

from api.dependencies.principal import current_account
from repositories.data.account.account_models import Account
from repositories.data.llm.llm_models import LLMProviderConfig
from services import llm_provider_service

router = APIRouter()


@logger.catch()
@router.post('/provider/{provider_key}/config')
async def add(workspace_uid: str, provider_key: str, llm_provider_config: LLMProviderConfig,
              current_user: Account = Depends(current_account)) -> LLMProviderConfig:
    """
    添加LLM Provider配置
    :param workspace_uid: 空间UID
    :param provider_key: Provider Key
    :param llm_provider_config: LLMProviderConfig
    :param current_user: 当前用户
    :return: LLMProviderConfig
    """
    llm_provider_config = await llm_provider_service.add(current_user, workspace_uid, provider_key, llm_provider_config)
    return llm_provider_service.provider_config_desensitize(llm_provider_config)


@logger.catch()
@router.delete('/provider/{provider_key}/config')
async def delete(workspace_uid: str, provider_key: str, current_user: Account = Depends(current_account)) -> bool:
    """
    删除LLM Provider配置
    :param workspace_uid: 空间UID
    :param provider_key: Provider Key
    :param current_user: 当前用户
    :return: boolean
    """
    return await llm_provider_service.delete(current_user, workspace_uid, provider_key)


@logger.catch()
@router.get('/provider/all/config')
async def all_configured_provider_configs(workspace_uid: str,
                                          current_user: Account = Depends(current_account)) -> list[LLMProviderConfig]:
    """
    获取所有已配置LLM Provider
    :param workspace_uid: 空间UID
    :param current_user: 当前用户
    :return: LLMProviderConfig
    """
    llm_provider_configs = await llm_provider_service.all_configured(current_user, workspace_uid)
    return [llm_provider_service.provider_config_desensitize(llm_provider_config)
            for llm_provider_config in (llm_provider_configs or [])]


@logger.catch()
@router.get('/provider/{provider_key}/config')
async def detail(workspace_uid: str, provider_key: str,
                 current_user: Account = Depends(current_account)) -> LLMProviderConfig | None:
    """
    获取LLM Provider配置详情
    :param workspace_uid: 空间UID
    :param provider_key: Provider Key
    :param current_user: 当前用户
    :return: LLMProviderConfig
    """
    llm_provider_config = await llm_provider_service.detail(current_user, workspace_uid, provider_key)
    return llm_provider_service.provider_config_desensitize(llm_provider_config)
