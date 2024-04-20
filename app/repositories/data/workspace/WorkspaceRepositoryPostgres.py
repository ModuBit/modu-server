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

import functools
import os

from sqlalchemy import PrimaryKeyConstraint, String, text, Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, Session

from repositories.data.database import with_async_session, BasePO
from repositories.data.database_postgres import PostgresBasePO
from repositories.data.workspace import WorkspaceRepository
from repositories.data.workspace.workspace_models import WorkspaceMemberStatus, WorkspaceMemberRole, Workspace, WorkspaceMembership
from repositories.data.type_decorator import Bool2SmallInt, Bytes2String
from utils.errors.space_error import SpaceCreationError


class WorkspaceRepositoryPostgres(WorkspaceRepository):
    """
    空间数据存储的PostgreSQL实现
    """

    @with_async_session
    async def create(self, workspace: Workspace, session: AsyncSession) -> Workspace:
        workspace_po = WorkspacePO(**vars(workspace))
        workspace_po.uid = BasePO.uid_generate()
        session.add(workspace_po)
        session.add(SpaceMembershipPO(workspace_uid=workspace_po.uid,
                                      member_uid=workspace.creator_uid,
                                      member_role=WorkspaceMemberRole.OWNER,
                                      member_status=WorkspaceMemberStatus.ACTIVE))
        workspace.uid = workspace_po.uid
        return workspace

    @with_async_session
    async def add_workspace_membership(
            self, workspace_uid: str, member_uid: str, role: WorkspaceMemberRole,
            session: AsyncSession) -> WorkspaceMembership:
        if role == WorkspaceMemberRole.OWNER:
            raise SpaceCreationError(message='无法添加为空间OWNER')

        membership_po = SpaceMembershipPO(workspace_uid=workspace_uid, member_uid=member_uid,
                                          member_role=role, member_status=WorkspaceMemberStatus.PENDING)
        session.add(membership_po)
        return WorkspaceMembership(**membership_po.as_dict())


class WorkspacePO(PostgresBasePO):
    """
    空间PO
    """

    __tablename__ = 'cube_workspace'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    creator_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='创建者uid')
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment='空间名称')
    description: Mapped[str] = mapped_column(String(512), nullable=True, comment='空间描述')
    is_personal: Mapped[bool] = mapped_column(Bool2SmallInt, nullable=False,
                                              server_default=text('0'),
                                              comment='是否为个人空间')
    iv: Mapped[bytes] = mapped_column(Bytes2String, nullable=False,
                                      default=functools.partial(os.urandom, 16), comment='初始向量')
    is_deleted: Mapped[bool] = mapped_column(Bool2SmallInt, nullable=False,
                                             server_default=text('0'),
                                             comment='是否已删除')


class SpaceMembershipPO(PostgresBasePO):
    """
    空间成员PO
    """

    __tablename__ = 'cube_workspace_membership'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    workspace_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='空间uid')
    member_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='成员uid')
    member_role: Mapped[WorkspaceMemberRole] = mapped_column(
        Enum(WorkspaceMemberRole, native_enum=False), nullable=False,
        server_default=text("'member'::character varying"),
        comment='成员角色')
    member_status: Mapped[WorkspaceMemberStatus] = mapped_column(
        Enum(WorkspaceMemberStatus, native_enum=False), nullable=False,
        server_default=text("'active'::character varying"),
        comment='成员状态')
