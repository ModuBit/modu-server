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

from llm.model import model_provider_factory
from repositories.cache import cache_decorator_builder
from repositories.cache.cache import CacheDecorator
from repositories.data import bot_repository, database
from repositories.data.account.account_models import Account
from repositories.data.bot.BotRepository import BotListQry
from repositories.data.bot.bot_models import Bot, BotMode
from repositories.data.publish.publish_config import PublishConfigTargetType
from services import workspace_service, account_service, publish_service
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
        raise UnauthorizedError("您无该空间权限")

    bot.workspace_uid = workspace_uid
    bot.creator_uid = current_user.uid

    if not bot.mode:
        bot.mode = BotMode.SINGLE_AGENT

    return await bot_repository.create(bot)


@bot_detail_cache.async_cache_evict(
    key_generator=lambda workspace_uid, bot_uid, **kwargs: f"workspace:{workspace_uid}:bot:{bot_uid}"
)
async def update_base_info(
    current_user: Account, workspace_uid: str, bot_uid: str, bot: Bot
) -> Bot:
    """
    更新机器人/智能体的配置
    :param current_user: 当前用户
    :param workspace_uid: 空间UID
    :param bot_uid: 机器人/智能体UID
    :param bot: 机器人/智能体
    :return: Bot
    """
    bot_detail = await detail(current_user, workspace_uid, bot_uid)
    if not bot_detail:
        raise UnauthorizedError("机器人/智能体不存在")
    if bot_detail.creator_uid != current_user.uid:
        raise UnauthorizedError("您无该机器人/智能体的权限")

    bot.uid = bot_uid
    return await bot_repository.update_base_info(bot)


@bot_detail_cache.async_cache_evict(
    key_generator=lambda workspace_uid, bot_uid, **kwargs: f"workspace:{workspace_uid}:bot:{bot_uid}"
)
async def update_bot_config(
    current_user: Account, workspace_uid: str, bot_uid: str, bot: Bot
) -> Bot:
    """
    更新机器人/智能体的配置
    :param current_user: 当前用户
    :param workspace_uid: 空间UID
    :param bot_uid: 机器人/智能体UID
    :param bot: 机器人/智能体
    :return: Bot
    """
    bot_detail = await detail(current_user, workspace_uid, bot_uid)
    if not bot_detail:
        raise UnauthorizedError("机器人/智能体不存在")
    if bot_detail.creator_uid != current_user.uid:
        raise UnauthorizedError("您无该机器人/智能体的权限")

    bot.uid = bot_uid
    return await bot_repository.update_bot_config(bot)


@bot_detail_cache.async_cacheable(
    key_generator=lambda workspace_uid, bot_uid, **kwargs: f"workspace:{workspace_uid}:bot:{bot_uid}"
)
async def detail(current_user: Account, workspace_uid: str, bot_uid: str) -> Bot:
    """
    查找单个机器人/智能体
    :param current_user: 当前用户
    :param workspace_uid: 空间UID
    :param bot_uid: 机器人/智能体UID
    :return: Bot
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError("您无该空间权限")

    bot = await bot_repository.get_by_workspace_and_uid(workspace_uid, bot_uid)
    if bot:
        bot.creator = await account_service.get_account_info(bot.creator_uid)

    return bot


async def find(
    current_user: Account, workspace_uid: str, bot_list_query: BotListQry
) -> list[Bot]:
    """
    查找某智能体前的智能体列表
    :param current_user: 当前用户
    :param workspace_uid: 空间ID
    :param bot_list_query: 查询条件
    """
    member_role = await workspace_service.member_role(current_user, workspace_uid)
    if member_role is None:
        raise UnauthorizedError("您无该空间权限")

    bots = await bot_repository.find(workspace_uid, bot_list_query)
    creators = await account_service.get_account_infos(
        list(set([bot.creator_uid for bot in bots]))
    )
    for bot in bots:
        bot.creator = creators[bot.creator_uid]

    return bots


async def save_config(
    current_user: Account,
    workspace_uid: str,
    bot_uid: str,
    bot_mode: BotMode,
    bot_config: dict,
) -> str:
    """
    保存机器人/智能体的配置
    :param current_user: 当前用户
    :param workspace_uid: 空间UID
    :param bot_uid: 机器人/智能体UID
    :param bot_mode: 机器人/智能体的模式
    :param bot_config: 机器人/智能体的配置
    :return: str
    """
    bot = await detail(current_user, workspace_uid, bot_uid)
    if not bot:
        raise UnauthorizedError("机器人/智能体不存在")
    if bot.creator_uid != current_user.uid:
        raise UnauthorizedError("您无该机器人/智能体的权限")

    return await publish_service.save(
        PublishConfigTargetType.BOT_CONFIG, bot_uid, bot_mode, bot_config
    )


@bot_detail_cache.async_cache_evict(
    key_generator=lambda workspace_uid, bot_uid, **kwargs: f"workspace:{workspace_uid}:bot:{bot_uid}"
)
async def publish_config(
    current_user: Account,
    workspace_uid: str,
    bot_uid: str,
    bot_mode: BotMode,
    bot_config: dict,
) -> str:
    """
    保存机器人/智能体的配置
    :param current_user: 当前用户
    :param workspace_uid: 空间UID
    :param bot_uid: 机器人/智能体UID
    :param bot_mode: 机器人/智能体的模式
    :param bot_config: 机器人/智能体的配置
    :return: str
    """
    bot = await detail(current_user, workspace_uid, bot_uid)
    if not bot:
        raise UnauthorizedError("机器人/智能体不存在")
    if bot.creator_uid != current_user.uid:
        raise UnauthorizedError("您无该机器人/智能体的权限")

    # 显式使用session（存在多个写动作，保证事务一致性）
    async with database.async_session() as session:
        publish_uid = await publish_service.publish(
            PublishConfigTargetType.BOT_CONFIG, bot_uid, bot_mode, bot_config, session
        )

        # 更新到 BOT
        await bot_repository.update_bot_config(
            bot_uid, bot_mode, bot_config, publish_uid, session
        )

    return publish_uid
