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

from typing import Mapping

from services import file_service
from config import app_config
from repositories.cache import cache_decorator_builder
from repositories.cache.cache import CacheDecorator, none_content
from repositories.data import account_repository
from repositories.data.account.account_models import (
    Account,
    AccountBaseInfo,
    AccountInfo,
)
from utils import auth
from utils.errors.account_error import AccountLoginError
from utils.json import default_excluded_fields

account_info_cache: CacheDecorator[AccountInfo] = cache_decorator_builder.build(
    serialize=lambda workspace: workspace.model_dump_json(
        exclude=default_excluded_fields
    ),
    deserialize=lambda json_content: AccountInfo.model_validate_json(json_content),
    default_expire_seconds=24 * 3600,
    allow_none_values=True,
)


async def authenticate(email: str, password: str) -> Account:
    """
    账号认证
    :param email: 邮箱
    :param password: 密码
    :return: 账号信息
    """

    account = await account_repository.find_one_by_email(email)

    if not account:
        raise AccountLoginError(message="用户名或密码错误")

    if not auth.verify_password(password, account.password):
        raise AccountLoginError(message="用户名或密码错误")

    account.password = None
    return account


def account_token_encode(account: Account) -> str:
    """
    账号 → token
    :param account: 账号信息
    :return: token
    """
    security_config = app_config.security
    jwt_config = security_config.jwt
    return auth.jose_encode(
        vars(account),
        security_config.secret,
        jwt_config.algorithm,
        jwt_config.expire_minutes,
    )


def account_token_decode(token: str) -> Account:
    """
    token → 账号
    :param token: token
    :return: 账号
    """
    security_config = app_config.security
    jwt_config = security_config.jwt
    account = auth.jose_decode(token, security_config.secret, jwt_config.algorithm)
    return Account(**account)


def account_token_verify(token: str):
    """
    验证token
    :param token: token
    """
    account_token_decode(token)


@account_info_cache.async_cache_evict(
    key_generator=lambda current_user, **kwargs: f"account:{current_user.uid}:info"
)
async def update_base_info(
    current_user: Account, user_info: AccountBaseInfo
) -> Account:
    """
    更新账号信息
    """
    user_info.uid = current_user.uid
    await account_repository.update_base_info(user_info)
    return await get_account_info(current_user.uid)


@account_info_cache.async_cacheable(
    key_generator=lambda uid, **kwargs: f"account:{uid}:info"
)
async def get_account_info(uid: str) -> AccountInfo:
    """
    查找账号信息
    :param uid: 账号 UID
    :return: AccountInfo
    """
    account = await account_repository.find_one_by_uid(uid)
    account_info = AccountInfo.model_validate(account) if account else None
    if account_info.avatar:
        account_info.avatar_url = await file_service.get_file_url_by_key(account_info.avatar)
    return account_info


async def get_account_infos(uids: list[str]) -> Mapping[str, AccountInfo]:
    """
    查找账号信息列表
    :param uids: 账号 UIDs
    :return: AccountInfo
    """
    # TODO 是否将列表缓存做成通用工具
    account_infos = {}
    uncached_uids = []
    account_info_caches = await account_info_cache.cache.mget(
        [f"account:{uid}:info" for uid in uids]
    )

    # 先查询已经缓存的
    for i in range(len(account_info_caches)):
        cached_content = account_info_caches[i]
        if not cached_content:
            uncached_uids.append(uids[i])
            continue

        if isinstance(cached_content, bytes):
            cached_content = cached_content.decode("utf-8")
        if none_content == cached_content:
            uncached_uids.append(uids[i])
            continue

        account_info = account_info_cache.deserialize(cached_content)
        account_infos[uids[i]] = account_info

    # 再查询未缓存的
    if uncached_uids:
        accounts = await account_repository.find_by_uids(uncached_uids)
        for account in accounts:
            account_info = AccountInfo.model_validate(account)
            account_infos[account.uid] = account_info
            await account_info_cache.cache.set(
                f"account:{account.uid}:info",
                account_info_cache.serialize(account_info),
                account_info_cache.default_expire_time,
            )

    return account_infos
