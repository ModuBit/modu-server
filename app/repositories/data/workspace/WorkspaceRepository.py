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

from .workspace_models import Workspace, WorkspaceMemberRole, WorkspaceMembership
from repositories.data.database import Repository, Database


class WorkspaceRepository(Repository):
    """
    空间数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def create(self, workspace: Workspace, session: AsyncSession) -> Workspace:
        """
        创建空间
        :param workspace: 空间
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def add_workspace_membership(
        self,
        workspace_uid: str,
        member_uid: str,
        role: WorkspaceMemberRole,
        session: AsyncSession,
    ) -> WorkspaceMembership:
        """
        添加空间成员
        :param workspace_uid: 空间UID
        :param member_uid: 成员UID
        :param role: 成员角色
        :param session: Session
        """
        raise NotImplementedError()

    @abstractmethod
    async def find_mine_by_creator_uid(
        self, creator_uid: str, session: AsyncSession
    ) -> Workspace:
        """
        查询私有空间
        :param creator_uid: 人员uid
        :param session: Session
        :return Workspace
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_by_uid(self, uid: str, session: AsyncSession) -> Workspace:
        """
        通过uid查询空间
        :param uid: 空间uid
        :return Workspace
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_member_by_uid(
        self, workspace_uid: str, member_uid: str, session: AsyncSession
    ) -> WorkspaceMembership:
        """
        通过uid查询空间成员
        :param workspace_uid: 空间uid
        :param member_uid: 成员uid
        :return Workspace
        """
        raise NotImplementedError()

    @abstractmethod
    async def is_member(
        self, workspace_uid: str, account_uid: str, session: AsyncSession
    ) -> bool:
        """
        判断是否是空间成员
        :param workspace_uid: 空间uid
        :param account_uid: 成员uid
        :return True False
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_member_role(
        self, workspace_uid: str, account_uid: str, session: AsyncSession
    ) -> WorkspaceMemberRole:
        """
        获取空间成员角色
        :param workspace_uid: 空间uid
        :param account_uid: 成员uid
        :return WorkspaceMemberRole
        """
        raise NotImplementedError()
