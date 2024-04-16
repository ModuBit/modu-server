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

from .team_models import Team, TeamMemberRole, TeamMembership
from ..database import Repository, Database


class TeamRepository(Repository):
    """
    团队数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def create(self, team: Team, session: AsyncSession) -> Team:
        """
        创建团队
        :param team: 团队
        :param session: Session
        """
        raise NotImplementedError

    @abstractmethod
    async def add_team_membership(
            self, team_uid: str, member_uid: str, role: TeamMemberRole,
            session: AsyncSession) -> TeamMembership:
        """
        添加团队成员
        :param team_uid: 团队UID
        :param member_uid: 成员UID
        :param role: 成员角色
        :param session: Session
        """
        raise NotImplementedError
