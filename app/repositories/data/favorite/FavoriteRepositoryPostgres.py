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

from typing import List
from sqlalchemy import (
    PrimaryKeyConstraint,
    String,
    delete,
    func,
    text,
    Enum,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from repositories.data.favorite.favorite_models import FavoriteTargetType
from repositories.data.database import with_async_session, BasePO
from repositories.data.postgres_database import PostgresBasePO
from repositories.data.favorite.FavoriteRepository import FavoriteRepository


class FavoriteRepositoryPostgres(FavoriteRepository):
    """
    收藏数据存储的PostgreSQL实现
    """

    @with_async_session
    async def favorite(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uid: str,
        session: AsyncSession,
    ) -> bool:
        is_favorite = await self.is_favorite(creator_uid, target_type, target_uid)
        if is_favorite:
            return True

        favorite_po = FavoritePO(
            target_type=target_type,
            target_uid=target_uid,
            creator_uid=creator_uid,
        )
        favorite_po.uid = BasePO.uid_generate()
        session.add(favorite_po)
        return True

    @with_async_session
    async def un_favorite(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uid: str,
        session: AsyncSession,
    ) -> bool:
        stmt = (
            delete(FavoritePO)
            .where(FavoritePO.creator_uid == creator_uid)
            .where(FavoritePO.target_type == target_type)
            .where(FavoritePO.target_uid == target_uid)
        )
        await session.execute(stmt)
        return True
    
    @with_async_session
    async def is_favorite(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uid: str,
        session: AsyncSession,
    ) -> bool:
        stmt = (
            select(func.count())
            .select_from(FavoritePO)
            .where(FavoritePO.creator_uid == creator_uid)
            .where(FavoritePO.target_type == target_type)
            .where(FavoritePO.target_uid == target_uid)
        )
        count_result = await session.execute(stmt)
        return count_result.scalar() > 0

    @with_async_session
    async def is_favorites(
        self,
        creator_uid: str,
        target_type: FavoriteTargetType,
        target_uids: List[str],
        session: AsyncSession,
    ) -> dict[str, bool]:
        if not target_uids:
            return {}
        stmt = (
            select(FavoritePO.target_uid)
            .where(FavoritePO.creator_uid == creator_uid)
            .where(FavoritePO.target_type == target_type)
            .where(FavoritePO.target_uid.in_(target_uids))
        )
        result = await session.execute(stmt)
        favorite_uids = set(result.scalars())
        return {target_uid: target_uid in favorite_uids for target_uid in target_uids}


class FavoritePO(PostgresBasePO):
    """
    收藏
    """

    __tablename__ = "modu_favorites"
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_id"),)

    target_type: Mapped[FavoriteTargetType] = mapped_column(
        Enum(FavoriteTargetType, native_enum=False),
        nullable=False,
        server_default=text("'BOT'::character varying"),
        comment="目标类型",
    )
    target_uid: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="目标uid"
    )
    creator_uid: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="创建者uid"
    )
