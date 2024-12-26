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
from services.account_service import AccountInfo
from utils.pydantic import CamelCaseJSONResponse

router = APIRouter()


@logger.catch()
@router.get(
    path="/me", response_model=AccountInfo, response_class=CamelCaseJSONResponse
)
async def me(current_user: Account = Depends(current_account)) -> Account:
    """
    当前登录人信息
    """
    return current_user
