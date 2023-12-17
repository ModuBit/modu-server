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
from abc import ABC
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from repositories.data.team.team_models import Team, TeamMemberRole


class TeamRepository(ABC):
    """
    团队数据存储的定义
    """

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self._session_factory = session_factory

    def create(self, team: Team):
        """
        创建团队
        :param team: 团队
        """
        raise NotImplementedError

    def add_team_membership(self, team_uid: str, member_uid: str, role: TeamMemberRole):
        """
        添加团队成员
        :param team_uid: 团队UID
        :param member_uid: 成员UID
        :param role: 成员角色
        :return:
        """
        raise NotImplementedError
