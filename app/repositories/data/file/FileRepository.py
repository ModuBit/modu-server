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

from abc import abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.data.file.file_models import File
from repositories.data.database import Database, Repository


class FileRepository(Repository):
    """
    文件数据存储的定义
    """

    def __init__(self, database: Database):
        super().__init__(database)

    @abstractmethod
    async def create_file(self, file: File, session: AsyncSession) -> File:
        """
        创建文件
        :param file: 文件
        :param session: 数据库会话
        :return: 文件
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_file_by_key(self, file_key: str, session: AsyncSession) -> File:
        """
        获取文件
        :param file_key: 文件KEY
        :param session: 数据库会话
        :return: 文件
        """
        raise NotImplementedError()
    
    @abstractmethod
    async def get_file_by_uid(self, file_uid: str, session: AsyncSession) -> File:
        """
        获取文件
        :param file_uid: 文件UID
        :param session: 数据库会话
        :return: 文件
        """
        raise NotImplementedError()
