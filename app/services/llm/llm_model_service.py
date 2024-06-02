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
from collections import defaultdict

from llm.model import model_provider_factory
from llm.model.entities.model import ModelSchema, ModelType
from repositories.data.account.account_models import Account
from services import workspace_service
from utils.errors.base_error import UnauthorizedError
from utils.errors.llm_error import LLMExistsError


async def all_models_from_provider(current_user: Account,
                                   workspace_uid: str, provider_name: str, ) -> dict[ModelType, list[ModelSchema]]:
    """
    获取空间下某一Provider的所有模型
    :param current_user: 当前用户
    :param workspace_uid: 工作空间UID
    :param provider_name: Provider Name
    :return: ModelSchema
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该权限查看')

    models: dict[ModelType, list[ModelSchema]] = defaultdict(list)

    # 来自 系统预配置
    llm_provider = model_provider_factory.get_provider(provider_name)
    if not llm_provider:
        raise LLMExistsError('LLM供应商不存在')

    for model in llm_provider.models or []:
        models[model.model_type].extend(model.model_schemas)

    # TODO 来自 用户自定义

    return models
