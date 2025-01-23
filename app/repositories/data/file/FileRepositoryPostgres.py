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

from repositories.data.database import with_async_session
from repositories.data.file.FileRepository import FileRepository
from repositories.data.file.file_models import File
from repositories.data.postgres_database import PostgresBasePO
from sqlalchemy import (
    Enum,
    Integer,
    PrimaryKeyConstraint,
    String,
    delete,
    func,
    select,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession


class FileRepositoryPostgres(FileRepository):
    """
    文件数据存储的PostgreSQL实现
    """

    @with_async_session
    async def create_file(self, file: File, session: AsyncSession) -> File:
        file_po = FilePO(**vars(file))
        session.add(file_po)
        return file

    @with_async_session
    async def get_file_by_key(self, file_key: str, session: AsyncSession) -> File:
        stmt = select(FilePO).where(FilePO.file_key == file_key).where(FilePO.is_deleted == False)
        result = await session.execute(stmt)
        file_po = result.scalars().one_or_none()
        return File(**file_po.as_dict()) if file_po else None
    
    @with_async_session
    async def get_file_by_keys(self, file_keys: list[str], session: AsyncSession) -> list[File]:
        if not file_keys:
            return []
        
        stmt = select(FilePO).where(FilePO.file_key.in_(file_keys)).where(FilePO.is_deleted == False)
        select_result = await session.execute(stmt)
        return [File(**conv.as_dict()) for conv in select_result.scalars()]
    
    @with_async_session
    async def get_file_by_uid(self, file_uid: str, session: AsyncSession) -> File:
        stmt = select(FilePO).where(FilePO.file_uid == file_uid).where(FilePO.is_deleted == False)
        result = await session.execute(stmt)
        file_po = result.scalars().one_or_none()
        return File(**file_po.as_dict()) if file_po else None


class FilePO(PostgresBasePO):
    """
    文件
    """

    __tablename__ = "modu_files"
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_id"),)

    file_key: Mapped[str] = mapped_column(String(64), nullable=False, comment="文件KEY")
    filename: Mapped[str] = mapped_column(String(256), nullable=False, comment="文件名")
    file_mime_type: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="文件MIME类型"
    )
    file_category: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="文件分类"
    )
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="文件大小")
    file_hash: Mapped[str] = mapped_column(
        String(256), nullable=False, comment="文件哈希"
    )
    storage_type: Mapped[str] = mapped_column(
        String(256), nullable=False, comment="存储类型"
    )
    creator_uid: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="创建者uid"
    )
