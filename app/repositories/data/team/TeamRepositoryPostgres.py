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
from sqlalchemy import PrimaryKeyConstraint, String, text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.data_base_postgres import PostgresBasePO, SmallIntBool
from repositories.data.team.TeamRepository import TeamRepository
from repositories.data.team.team_models import TeamMemberStatus, TeamMemberRole, Team
from utils.errors.team_error import TeamCreationError


class TeamRepositoryPostgres(TeamRepository):
    """
    团队数据存储的PostgreSQL实现
    """

    def create(self, team: Team):
        with self._session_factory() as session:
            team_po = TeamPO(**team.__dict__)
            session.add(team_po)
            session.commit()
            session.add(TeamMembershipPO(team_uid=team_po.uid,
                                         member_uid=team.creator_uid,
                                         member_role=TeamMemberRole.OWNER,
                                         member_status=TeamMemberStatus.ACTIVE))
            session.commit()

    def add_team_membership(self, team_uid: str, member_uid: str, role: TeamMemberRole):
        if role == TeamMemberRole.OWNER:
            raise TeamCreationError(message='无法添加为团队OWNER')

        with self._session_factory() as session:
            session.add(TeamMembershipPO(team_uid=team_uid, member_uid=member_uid,
                                         role=role, status=TeamMemberStatus.PENDING))
            session.commit()


class TeamPO(PostgresBasePO):
    """
    团队PO
    """

    __tablename__ = 'cube_teams'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    creator_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='创建者uid')
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment='团队名称')
    description: Mapped[str] = mapped_column(String(512), nullable=True, comment='团队描述')
    is_personal: Mapped[bool] = mapped_column(SmallIntBool, nullable=False,
                                              server_default=text('0'),
                                              comment='是否为个人团队')
    is_deleted: Mapped[bool] = mapped_column(SmallIntBool, nullable=False,
                                             server_default=text('0'),
                                             comment='是否已删除')


class TeamMembershipPO(PostgresBasePO):
    """
    团队成员PO
    """

    __tablename__ = 'cube_team_memberships'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    team_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='团队uid')
    member_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='成员uid')
    member_role: Mapped[TeamMemberRole] = mapped_column(Enum(TeamMemberRole), nullable=False,
                                                        server_default=text("'member'::character varying"),
                                                        comment='成员角色')
    member_status: Mapped[TeamMemberStatus] = mapped_column(Enum(TeamMemberStatus), nullable=False,
                                                            server_default=text("'active'::character varying"),
                                                            comment='成员状态')
