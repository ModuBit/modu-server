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
from llm.model.entities.model import ModelSchema, ModelType
from repositories.data.account.account_models import Account
from services import llm_model_service

router = APIRouter()


@logger.catch()
@router.post('/provider/{provider_name}/model')
async def models(workspace_uid: str, provider_name: str,
                 current_user: Account = Depends(current_account)) -> dict[ModelType, list[ModelSchema]]:
    """
    获取空间下某一Provider的所有模型
    :param workspace_uid: 工作空间UID
    :param provider_name: Provider Name
    :param current_user: 当前用户
    :return: ModelSchema
    """
    return await llm_model_service.all_models_from_provider(current_user, workspace_uid, provider_name)
