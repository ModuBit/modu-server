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

import datetime
import os
from abc import ABC, abstractmethod
from typing import AsyncGenerator, BinaryIO, Generator


class Storage(ABC):
    """
    存储基类
    """

    @abstractmethod
    async def put_file(self, filename: str, data: bytes | str | BinaryIO) -> str:
        """
        上传文件
        :param filename: 文件名
        :param data: 文件内容
        """
        raise NotImplementedError()
    
    @abstractmethod
    async def get_file_bytes(self, file_key: str) -> bytes:
        """
        获取文件字节
        :param file_key: 文件名
        :return: 文件字节
        """
        raise NotImplementedError()
        
    @abstractmethod
    async def get_stream(self, file_key: str) -> AsyncGenerator[bytes, None]:
        """
        获取文件流
        :param file_key: 文件名
        :return: 文件流
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete_file(self, file_key: str) -> bool:
        """
        删除文件
        :param file_key: 文件名
        """
        raise NotImplementedError()
    
    @abstractmethod
    async def exists_file(self, file_key: str) -> bool:
        """
        文件是否存在
        :param file_key: 文件名
        :return: 文件是否存在
        """
        raise NotImplementedError()

    @abstractmethod
    async def sign_url(self, file_key: str, expires: int) -> str:
        """
        生成文件签名URL
        :param file_key: 文件名
        :param expires: 过期时间(秒)
        """
        raise NotImplementedError()
    
    def _wrapper_date_folder(self, filename: str, *paths, sep: str = os.sep) -> str:
        """
        按照当前日期，将文件名包装为 [paths/]yyyy/mm/{filename}
        :param filename: 文件名
        :param paths: 父路径
        :param sep: 分隔符
        :return: 包装后的文件名
        """
        date_folder = datetime.datetime.now().strftime('%Y' + sep + '%m')
        if paths:
            # 如果有父路径，则拼接父路径、日期文件夹和文件名
            return os.path.join(*paths, date_folder, filename.lstrip(sep).rstrip(sep))
        # 如果没有父路径，则只拼接日期文件夹和文件名
        return os.path.join(date_folder, filename.lstrip(sep).rstrip(sep))
    
    async def close(self):
        """
        关闭存储
        """
        pass
