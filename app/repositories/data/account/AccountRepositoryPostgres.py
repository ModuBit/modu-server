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

from sqlalchemy import PrimaryKeyConstraint, String, Enum, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.postgres_database import PostgresBasePO
from utils.errors.account_error import AccountLoginError
from .AccountRepository import AccountRepository
from .account_models import Account, AccountStatus
from ..database import with_async_session, BasePO


class AccountRepositoryPostgres(AccountRepository):
    """
    账号数据存储的PostgreSQL实现
    """

    @with_async_session
    async def find_one_by_uid(self, uid: str, session: AsyncSession) -> Account | None:
        stmt = select(AccountPO).where(AccountPO.uid == uid).limit(1)
        select_result = await session.execute(stmt)
        account_model = select_result.scalars().one_or_none()
        return Account(**account_model.as_dict()) if account_model else None

    @with_async_session
    async def find_by_uids(
        self, uids: list[str], session: AsyncSession
    ) -> list[Account]:
        if not uids:
            return []
        stmt = select(AccountPO).where(AccountPO.uid.in_(uids))
        select_result = await session.execute(stmt)
        return [Account(**conv.as_dict()) for conv in select_result.scalars()]

    @with_async_session
    async def find_one_by_email(self, email: str, session: AsyncSession) -> Account:
        stmt = (
            select(AccountPO)
            .where(AccountPO.email == email)
            .where(AccountPO.is_deleted == False)
            .limit(1)
        )
        select_result = await session.execute(stmt)
        account_model = select_result.scalars().one_or_none()
        if not account_model:
            raise AccountLoginError(message="邮箱或密码错误")
        return Account(**account_model.as_dict())

    @with_async_session
    async def create(
        self, name: str, email: str, password: str, session: AsyncSession
    ) -> Account:
        account_po = AccountPO(
            name=name, email=email, password=password, status=AccountStatus.ACTIVE
        )
        account_po.uid = BasePO.uid_generate()
        session.add(account_po)

        return Account(**account_po.as_dict())

    @with_async_session
    async def count_all(self, session: AsyncSession) -> int:
        stmt = (
            select(func.count())
            .select_from(AccountPO)
            .where(AccountPO.is_deleted == False)
        )
        count_result = await session.execute(stmt)
        return count_result.scalar()


class AccountPO(PostgresBasePO):
    """
    账号PO
    """

    __tablename__ = "modu_accounts"
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_id"),)

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(String(128), nullable=False, comment="邮箱")
    password: Mapped[str] = mapped_column(String(128), nullable=False, comment="密码")
    avatar: Mapped[str] = mapped_column(String(256), nullable=True, comment="头像")
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, native_enum=False),
        nullable=False,
        server_default=text("'active'::character varying"),
        comment="账号状态",
    )
