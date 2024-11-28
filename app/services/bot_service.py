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

from repositories.cache import cache_decorator_builder
from repositories.cache.cache import CacheDecorator
from repositories.data import bot_repository
from repositories.data.account.account_models import Account
from repositories.data.bot.BotRepository import BotListQry
from repositories.data.bot.bot_models import Bot, BotMode
from services import workspace_service, account_service
from utils.errors.base_error import UnauthorizedError

bot_detail_cache: CacheDecorator[Bot] = cache_decorator_builder.build(
    serialize=lambda workspace: workspace.model_dump_json(),
    deserialize=lambda json_content: Bot.model_validate_json(json_content),
    default_expire_seconds=7 * 24 * 3600,
    allow_none_values=True,
)


async def add(current_user: Account, workspace_uid: str, bot: Bot) -> Bot:
    """
    添加 机器人/智能体
    :param current_user: 当前用户
    :param workspace_uid: 空间UID
    :param bot: 机器人/智能体
    :return: Bot
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该空间权限')

    bot.workspace_uid = workspace_uid
    bot.creator_uid = current_user.uid

    if not bot.mode:
        bot.mode = BotMode.SINGLE_AGENT

    return await bot_repository.create(bot)


async def find(current_user: Account, workspace_uid: str, bot_list_query: BotListQry) -> list[Bot]:
    """
    查找某智能体前的智能体列表
    :param current_user: 当前用户
    :param workspace_uid: 空间ID
    :param bot_list_query: 查询条件
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError('您无该空间权限')

    bots = await bot_repository.find(workspace_uid, bot_list_query)
    creators = await account_service.get_account_infos(list(set([bot.creator_uid for bot in bots])))
    for bot in bots:
        bot.creator = creators[bot.creator_uid]

    return bots