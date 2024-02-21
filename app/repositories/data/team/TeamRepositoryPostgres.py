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

import os

from sqlalchemy import PrimaryKeyConstraint, String, text, Enum
from sqlalchemy.orm import Mapped, mapped_column, Session

from repositories.data.database import with_session, BasePO
from repositories.data.database_postgres import PostgresBasePO
from repositories.data.team import TeamRepository
from repositories.data.team.team_models import TeamMemberStatus, TeamMemberRole, Team, TeamMembership
from repositories.data.type_decorator import Bool2SmallInt, Bytes2String
from utils.errors.team_error import TeamCreationError


class TeamRepositoryPostgres(TeamRepository):
    """
    团队数据存储的PostgreSQL实现
    """

    @with_session
    def create(self, team: Team, session: Session) -> Team:
        team_po = TeamPO(**team.__dict__)
        team_po.uid = BasePO.uid_generate()
        session.add(team_po)
        session.add(TeamMembershipPO(team_uid=team_po.uid,
                                     member_uid=team.creator_uid,
                                     member_role=TeamMemberRole.OWNER,
                                     member_status=TeamMemberStatus.ACTIVE))
        team.uid = team_po.uid
        return team

    @with_session
    def add_team_membership(self, team_uid: str, member_uid: str, role: TeamMemberRole, session: Session) -> TeamMembership:
        if role == TeamMemberRole.OWNER:
            raise TeamCreationError(message='无法添加为团队OWNER')

        membership_po = TeamMembershipPO(team_uid=team_uid, member_uid=member_uid,
                                         role=role, status=TeamMemberStatus.PENDING)
        session.add(membership_po)
        return TeamMembership(**membership_po.as_dict())


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
    is_personal: Mapped[bool] = mapped_column(Bool2SmallInt, nullable=False,
                                              server_default=text('0'),
                                              comment='是否为个人团队')
    iv: Mapped[bytes] = mapped_column(Bytes2String, nullable=False,
                                      default=lambda _: os.urandom(16), comment='初始向量')
    is_deleted: Mapped[bool] = mapped_column(Bool2SmallInt, nullable=False,
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
