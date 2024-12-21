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
from pydantic import BaseModel

from api.dependencies.principal import current_account
from repositories.data.account.account_models import Account, AccountInfo
from repositories.data.bot.BotRepository import BotListQry
from repositories.data.bot.bot_models import Bot, BotMode
from services import bot_service
from utils.pydantic import CamelCaseJSONResponse, default_model_config

router = APIRouter()


class BotDTO(BaseModel):
    uid: str | None = None
    """uid"""
    workspace_uid: str
    """空间UID"""
    name: str
    """名称"""
    avatar: str | None = None
    """头像"""
    description: str | None = None
    """描述"""
    creator_uid: str
    """创建人UID"""
    creator: AccountInfo | None = None
    """创建人"""
    mode: BotMode | None = None
    """模式"""
    publish_uid: str | None = None
    """发布UID"""

    # 定义配置
    model_config = default_model_config()


def get_bot_list_qry(
        keyword: Optional[str] = Query(None),
        mode: Optional[BotMode] = Query(None),
        is_published: Optional[bool] = Query(None),
        after_uid_limit: Optional[str] = Query(None),
        max_count: int = Query(20)) -> BotListQry:
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
@router.put('/{bot_uid}', response_class=CamelCaseJSONResponse)
async def update(workspace_uid: str, bot_uid: str, bot: Bot,
                 current_user: Account = Depends(current_account)) -> Bot:
    """
    修改 机器人/智能体
    :param workspace_uid: 空间UID
    :param bot: 机器人/智能体
    :param current_user: 当前用户
    :return: Bot
    """
    return await bot_service.update(current_user, workspace_uid, bot_uid, bot)


@logger.catch()
@router.get(path='/{bot_uid}', response_model=BotDTO, response_class=CamelCaseJSONResponse)
async def detail(workspace_uid: str, bot_uid: str, current_user: Account = Depends(current_account)) -> Bot:
    """
    查询 机器人/智能体
    :param workspace_uid: 空间UID
    :param bot_uid: 机器人/智能体的UID
    :param current_user: 当前用户
    :return: Bot
    """
    return await bot_service.detail(current_user, workspace_uid, bot_uid)


@logger.catch()
@router.get(path='', response_model=list[BotDTO], response_class=CamelCaseJSONResponse)
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
