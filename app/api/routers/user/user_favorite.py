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

from typing import Optional
from fastapi import APIRouter, Depends, Query
from loguru import logger

from api.dependencies.principal import current_account
from services import bot_service
from repositories.data.account.account_models import Account
from repositories.data.bot.bot_models import BotFavoriteDTO
from utils.pydantic import CamelCaseJSONResponse
from repositories.data.bot.BotRepository import BotFavoriteListQry


router = APIRouter()


################################################################################
# bot
################################################################################


def get_bot_favorite_list_qry(
    keyword: Optional[str] = Query(None),
    after_uid_limit: Optional[str] = Query(None),
    max_count: int = Query(20),
) -> BotFavoriteListQry:
    return BotFavoriteListQry(
        keyword=keyword,
        after_uid_limit=after_uid_limit,
        max_count=max_count,
    )


@logger.catch()
@router.get(
    path="/bots",
    response_model=list[BotFavoriteDTO],
    response_class=CamelCaseJSONResponse,
)
async def find_favorite_bots(
    bot_favorite_list_qry: BotFavoriteListQry = Depends(get_bot_favorite_list_qry),
    current_user: Account = Depends(current_account),
) -> list[BotFavoriteDTO]:
    """
    查询 智能体收藏列表
    :param bot_favorite_list_qry: 查询条件
    :param current_user: 当前用户
    :return: list[BotFavoriteDTO]
    """
    return await bot_service.find_favorite(
        current_user, bot_favorite_list_qry
    )
