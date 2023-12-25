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

from repositories.data.account.AccountRepository import AccountRepository
from repositories.data.account.account_models import Account, AccountStatus
from repositories.data.team.TeamRepository import TeamRepository
from repositories.data.team.team_models import Team
from utils.auth import hash_password
from utils.errors.base_error import ErrorShowType
from utils.errors.system_error import InitializeError


class InitService:
    """
    初始化服务
    """

    def __init__(self, account_repository: AccountRepository, team_repository: TeamRepository):
        self._account_repository = account_repository
        self._team_repository = team_repository

    def is_initialized(self) -> bool:
        """
        判断是否已经初始化
        :return: True / False
        """
        return self._account_repository.count_all() > 0

    def initialize(self, name: str, email: str, password: str):
        """
        初始化服务
        :param name: 名称
        :param email: 邮箱
        :param password: 密码
        """
        if self.is_initialized():
            raise InitializeError(
                message='已初始化，请直接登录', status_code=409,
                show_type=ErrorShowType.REDIRECT, target='/login', )

        # 创建账号
        self._account_repository.create(
            Account(name=name, email=email, password=hash_password(password), status=AccountStatus.ACTIVE))

        # 创建团队
        self._team_repository.create(
            Team(
                creator_uid=self._account_repository.find_one_by_email(email).uid,
                name=f'{name}的默认团队',
                description=f'{name}的默认团队',
                is_personal=True,
            )
        )
