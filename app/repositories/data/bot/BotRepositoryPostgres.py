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

from sqlalchemy import PrimaryKeyConstraint, String, Enum, text, delete, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.bot.BotRepository import BotRepository, BotListQry
from repositories.data.bot.bot_models import BotMode, Bot
from repositories.data.database import with_async_session, BasePO
from repositories.data.postgres_database import PostgresBasePO
from repositories.data.publish.PublishConfigRepositoryPostgres import Dict2Json


class BotRepositoryPostgres(BotRepository):
    """
    Bot数据存储的PostgreSQL实现
    """

    @with_async_session
    async def create(self, bot: Bot, session: AsyncSession) -> Bot:
        bot_po = BotPO(**vars(bot))
        bot_po.uid = BasePO.uid_generate()
        session.add(bot_po)
        bot.uid = bot_po.uid
        return bot

    @with_async_session
    async def find(self, workspace_uid: str, qry: BotListQry, session: AsyncSession) -> list[Bot]:
        stmt = (select(BotPO)
                .where(BotPO.workspace_uid == workspace_uid)
                .where(BotPO.is_deleted == False))

        # 搜索关键字
        if qry.keyword:
            stmt = stmt.where(or_(BotPO.name.ilike(f"%{qry.keyword}%"), BotPO.description.ilike(f"%{qry.keyword}%")))

        # 筛选模式
        if qry.mode:
            stmt = stmt.where(BotPO.mode == qry.mode)

        # 筛选已发布
        if qry.is_published:
            stmt = stmt.where(BotPO.publish_uid.isnot(None))

        # 筛选时间（信息流代替翻页）
        if qry.after_uid_limit:
            after_uid_subquery = (
                select(BotPO.created_at)
                .where(BotPO.uid == qry.after_uid_limit)
                .where(BotPO.is_deleted == False)
            ).scalar_subquery()
            stmt = stmt.where(BotPO.created_at < after_uid_subquery)

        stmt = stmt.order_by(BotPO.created_at.desc()).limit(qry.max_count)
        select_result = await session.execute(stmt)
        return [Bot(**conv.as_dict()) for conv in select_result.scalars()]

    @with_async_session
    async def get_by_uid(self, bot_uid: str, session: AsyncSession) -> Bot:
        stmt = (select(BotPO)
                .where(BotPO.uid == bot_uid)
                .where(BotPO.is_deleted == False)
                .limit(1))
        select_result = await session.execute(stmt)
        bot_model = select_result.scalars().one_or_none()
        return Bot(**bot_model.as_dict()) if bot_model else None

    @with_async_session
    async def delete_by_uid(self, bot_uid: str, session: AsyncSession) -> bool:
        stmt = delete(BotPO).where(BotPO.uid == bot_uid)
        await session.execute(stmt)
        return True


class BotPO(PostgresBasePO):
    """
    Bot PO
    """

    __tablename__ = 'modu_bots'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    workspace_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='所属空间uid')
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment='Bot名称')
    avatar: Mapped[str] = mapped_column(String(256), nullable=True, comment='头像')
    description: Mapped[str] = mapped_column(String(512), nullable=True, comment='描述')
    creator_uid: Mapped[str] = mapped_column(String(32), nullable=False, comment='创建者uid')
    mode: Mapped[BotMode] = mapped_column(Enum(BotMode, native_enum=False), nullable=False,
                                          server_default=text("'SINGLE_AGENT'::character varying"), comment='模式')
    config: Mapped[dict] = mapped_column(Dict2Json, nullable=True, comment='配置内容')
    publish_uid: Mapped[str] = mapped_column(String(32), nullable=True, comment='发布uid')
