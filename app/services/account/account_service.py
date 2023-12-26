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

from repositories.data.account import AccountRepository
from repositories.data.account.account_models import Account
from utils import auth
from utils.auth import hash_password
from utils.errors.account_error import AccountLoginError


class AccountService:
    """
    账号服务
    """

    def __init__(self, account_repository: AccountRepository, jwt_config: dict):
        self._account_repository = account_repository
        self._jwt_config = jwt_config

    def register(self, account: Account):
        # 创建账号
        self._account_repository.create(Account(**account.__dict__, password=hash_password(account.password)))

    def authenticate(self, email: str, password: str) -> Account:
        """
        账号认证
        :param email: 邮箱
        :param password: 密码
        :return: 账号信息
        """

        account = self._account_repository.find_one_by_email(email)

        if not account:
            raise AccountLoginError(message='用户名或密码错误')

        if not auth.verify_password(password, account.password):
            raise AccountLoginError(message='用户名或密码错误')

        # TODO 需要移除敏感信息
        return account

    def account_token_encode(self, account: Account) -> str:
        """
        账号 → token
        :param account: 账号信息
        :return: token
        """
        return auth.jose_encode(account.__dict__,
                                self._jwt_config.get('secret'),
                                self._jwt_config.get('algorithm'),
                                self._jwt_config.get('expire_minutes'))

    def account_token_decode(self, token: str) -> Account:
        """
        token → 账号
        :param token: token
        :return: 账号
        """
        return auth.jose_decode(token,
                                self._jwt_config.get('secret'),
                                self._jwt_config.get('algorithm'))

    def account_token_verify(self, token: str):
        """
        验证token
        :param token: token
        """
        auth.jose_decode(token,
                         self._jwt_config.get('secret'),
                         self._jwt_config.get('algorithm'))
