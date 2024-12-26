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

from abc import abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from .account_models import Account
from ..database import Repository, Database


class AccountRepository(Repository):
    """
    账号数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def find_one_by_uid(self, uid: str, session: AsyncSession) -> Account:
        """
        通过uid查找账号
        :param uid: UID
        :param session: Session
        :return: 账号
        """
        raise NotImplementedError()

    @abstractmethod
    async def find_by_uids(
        self, uids: list[str], session: AsyncSession
    ) -> list[Account]:
        """
        通过uid查找账号
        :param uids: UID
        :param session: Session
        :return: 账号
        """
        raise NotImplementedError()

    @abstractmethod
    async def find_one_by_email(self, email: str, session: AsyncSession) -> Account:
        """
        通过email查找账号
        :param email: 邮箱
        :param session: Session
        :return: 账号
        """
        raise NotImplementedError()

    @abstractmethod
    async def create(
        self, name: str, email: str, password: str, session: AsyncSession
    ) -> Account:
        """
        创建账号
        :param name: 用户名
        :param email: 邮箱
        :param password: 密码
        :param session: Session
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    async def count_all(self, session: AsyncSession) -> int:
        """
        统计所有账号
        :param session: Session
        :return: 账号数量
        """
        raise NotImplementedError()
