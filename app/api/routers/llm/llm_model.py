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
from itertools import groupby
from operator import attrgetter

from fastapi import APIRouter, Depends
from loguru import logger

from api.dependencies.principal import current_account
from llm.model.entities.model import ModelSchema, ModelType
from llm.model.entities.provider import ProviderWithModelsSchema
from repositories.data.account.account_models import Account
from services import llm_model_service

router = APIRouter()


@logger.catch()
@router.get('/provider/{provider_name}/model')
async def all_models_on_provider(workspace_uid: str, provider_name: str,
                                 current_user: Account = Depends(current_account)) -> dict[ModelType, list[ModelSchema]]:
    """
    获取空间下某一Provider的所有模型
    :param workspace_uid: 工作空间UID
    :param provider_name: Provider Name
    :param current_user: 当前用户
    :return: ModelSchema
    """
    provider_with_models = await llm_model_service.get_models(current_user, workspace_uid, provider_name)
    if not provider_with_models:
        return {}

    return provider_with_models[0].get_grouped_models_by_type()


@logger.catch()
@router.get(path='/model/type/{model_type}', response_model=list[ProviderWithModelsSchema])
async def all_models_on_type(workspace_uid: str, model_type: ModelType,
                             current_user: Account = Depends(current_account)) -> list[ProviderWithModelsSchema]:
    """
    获取空间下某一模型类型的所有模型
    :param workspace_uid: 工作空间UID
    :param model_type: 模型类型
    :param current_user: 当前用户
    :return: ModelSchema
    """
    return await llm_model_service.get_models(current_user, workspace_uid, model_type=model_type)
