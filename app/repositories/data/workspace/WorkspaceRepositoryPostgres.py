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

from sqlalchemy import PrimaryKeyConstraint, String, text, Enum, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.database import with_async_session, BasePO
from repositories.data.postgres_database import PostgresBasePO
from repositories.data.workspace import WorkspaceRepository
from repositories.data.workspace.workspace_models import WorkspaceMemberStatus, WorkspaceMemberRole, Workspace, \
    WorkspaceMembership, WorkspaceType
from utils.errors.space_error import SpaceCreationError, SpaceExistsError


class WorkspaceRepositoryPostgres(WorkspaceRepository):
    """
    空间数据存储的PostgreSQL实现
    """

    @with_async_session
    async def create(self, workspace: Workspace, session: AsyncSession) -> Workspace:
        workspace_po = WorkspacePO(**vars(workspace))
        workspace_po.uid = BasePO.uid_generate()
        session.add(workspace_po)
        session.add(WorkspaceMembershipPO(workspace_uid=workspace_po.uid,
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

        membership_po = WorkspaceMembershipPO(workspace_uid=workspace_uid, member_uid=member_uid,
                                              member_role=role, member_status=WorkspaceMemberStatus.PENDING)
        session.add(membership_po)
        return WorkspaceMembership(**membership_po.as_dict())

    @with_async_session
    async def find_mine_by_creator_uid(self, creator_uid: str, session: AsyncSession) -> Workspace:
        stmt = (select(WorkspacePO)
                .where(WorkspacePO.creator_uid == creator_uid)
                .where(WorkspacePO.is_deleted == False)
                .limit(1))
        select_result = await session.execute(stmt)
        workspace_model = select_result.scalars().one_or_none()
        if not workspace_model:
            raise SpaceExistsError(message='无私有空间，请联系管理员')
        return Workspace(**workspace_model.as_dict())

    @with_async_session
    async def get_by_uid(self, uid: str, session: AsyncSession) -> Workspace:
        stmt = (select(WorkspacePO)
                .where(WorkspacePO.uid == uid)
                .where(WorkspacePO.is_deleted == False)
                .limit(1))
        select_result = await session.execute(stmt)
        workspace_model = select_result.scalars().one_or_none()
        return Workspace(**workspace_model.as_dict()) if workspace_model else None

    @with_async_session
    async def get_member_by_uid(self, workspace_uid: str, member_uid: str,
                                session: AsyncSession) -> WorkspaceMembership:
        stmt = (select(WorkspaceMembershipPO)
                .where(WorkspaceMembershipPO.workspace_uid == workspace_uid)
                .where(WorkspaceMembershipPO.member_uid == member_uid)
                .where(WorkspacePO.is_deleted == False)
                .limit(1))
        select_result = await session.execute(stmt)
        workspace_member_model = select_result.scalars().one_or_none()
        return WorkspaceMembership(**workspace_member_model.as_dict()) if workspace_member_model else None

    @with_async_session
    async def is_member(self, workspace_uid: str, member_uid: str, session: AsyncSession) -> bool:
        stmt = (select(func.count()).select_from(WorkspaceMembershipPO)
                .where(WorkspaceMembershipPO.workspace_uid == workspace_uid)
                .where(WorkspaceMembershipPO.member_uid == member_uid)
                .where(WorkspacePO.is_deleted == False))
        count = await session.execute(stmt)
        return count.scalar() > 0

    @with_async_session
    async def get_member_role(
            self, workspace_uid: str, account_uid: str, session: AsyncSession) -> WorkspaceMemberRole | None:
        workspace = await self.get_by_uid(workspace_uid, session)
        if not workspace:
            return None

        # 创建人
        if workspace.creator_uid == account_uid:
            return WorkspaceMemberRole.OWNER

        workspace_member = await self.get_member_by_uid(workspace_uid, account_uid)
        if not workspace_member:
            return None

        # 成员
        return workspace_member.member_role


class WorkspacePO(PostgresBasePO):
    """
    空间PO
    """

    __tablename__ = 'modu_workspace'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    creator_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='创建者uid')
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment='空间名称')
    description: Mapped[str] = mapped_column(String(512), nullable=True, comment='空间描述')
    type: Mapped[WorkspaceType] = mapped_column(
        Enum(WorkspaceType, native_enum=False), nullable=False,
        comment='空间类型')


class WorkspaceMembershipPO(PostgresBasePO):
    """
    空间成员PO
    """

    __tablename__ = 'modu_workspace_membership'
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
