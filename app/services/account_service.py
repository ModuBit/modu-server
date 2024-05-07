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

from config import app_config
from repositories.data import account_repository
from repositories.data.account.account_models import Account
from utils import auth
from utils.errors.account_error import AccountLoginError


async def authenticate(email: str, password: str) -> Account:
    """
    账号认证
    :param email: 邮箱
    :param password: 密码
    :return: 账号信息
    """

    account = await account_repository.find_one_by_email(email)

    if not account:
        raise AccountLoginError(message='用户名或密码错误')

    if not auth.verify_password(password, account.password):
        raise AccountLoginError(message='用户名或密码错误')

    account.password = None
    return account


def account_token_encode(account: Account) -> str:
    """
    账号 → token
    :param account: 账号信息
    :return: token
    """
    jwt_config = app_config.security.jwt
    return auth.jose_encode(vars(account),
                            jwt_config.secret,
                            jwt_config.algorithm,
                            jwt_config.expire_minutes)


def account_token_decode(token: str) -> Account:
    """
    token → 账号
    :param token: token
    :return: 账号
    """
    jwt_config = app_config.security.jwt
    account = auth.jose_decode(token, jwt_config.secret, jwt_config.algorithm)
    return Account(**account)


def account_token_verify(token: str):
    """
    验证token
    :param token: token
    """
    account_token_decode(token)
