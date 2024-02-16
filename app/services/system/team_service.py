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

from repositories.data.team import TeamRepository
from repositories.data.team.team_models import Team, TeamMemberRole


class TeamService:
    """
    团队服务
    """

    def __init__(self, team_repository: TeamRepository):
        self._team_repository = team_repository

    def create(self, team: Team):
        self._team_repository.create(team)

    def add_team_membership(self, team_uid: str, member_uid: str, role: TeamMemberRole):
        self._team_repository.add_team_membership(
            team_uid, member_uid,
            TeamMemberRole.MEMBER if role == TeamMemberRole.OWNER else role)
