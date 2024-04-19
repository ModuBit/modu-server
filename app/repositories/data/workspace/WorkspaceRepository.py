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
from sqlalchemy.orm import Session

from .workspace_models import Workspace, WorkspaceMemberRole, WorkspaceMembership
from ..database import Repository, Database


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
        raise NotImplementedError

    @abstractmethod
    async def add_workspace_membership(
            self, workspace_uid: str, member_uid: str, role: WorkspaceMemberRole,
            session: AsyncSession) -> WorkspaceMembership:
        """
        添加空间成员
        :param workspace_uid: 空间UID
        :param member_uid: 成员UID
        :param role: 成员角色
        :param session: Session
        """
        raise NotImplementedError
