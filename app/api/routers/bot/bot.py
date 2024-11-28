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
from repositories.data.account.account_models import Account
from repositories.data.bot.BotRepository import BotListQry
from repositories.data.bot.bot_models import Bot, BotMode
from services import bot_service
from utils.pydantic import CamelCaseJSONResponse

router = APIRouter()


def get_bot_list_qry(
        keyword: Optional[str] = Query(None),
        mode: Optional[BotMode] = Query(None),
        is_published: Optional[bool] = Query(None, alias="isPublished"),
        after_uid_limit: Optional[str] = Query(None, alias="afterUidLimit"),
        max_count: int = Query(20, alias="maxCount")) -> BotListQry:
    return BotListQry(keyword=keyword,
                      mode=mode,
                      is_published=is_published,
                      after_uid_limit=after_uid_limit,
                      max_count=max_count)


@logger.catch()
@router.post('', response_class=CamelCaseJSONResponse)
async def add(workspace_uid: str, bot: Bot,
              current_user: Account = Depends(current_account)) -> Bot:
    """
    添加 机器人/智能体
    :param workspace_uid: 空间UID
    :param bot: 机器人/智能体
    :param current_user: 当前用户
    :return: Bot
    """
    return await bot_service.add(current_user, workspace_uid, bot)


@logger.catch()
@router.get(path='')
async def find(workspace_uid: str, bot_list_qry: BotListQry = Depends(get_bot_list_qry),
               current_user: Account = Depends(current_account)) -> list[Bot]:
    """
    查询 机器人/智能体 列表
    :param workspace_uid: 空间UID
    :param bot_list_qry: 查询条件
    :param current_user: 当前用户
    :return: Bot
    """
    return await bot_service.find(current_user, workspace_uid, bot_list_qry)
