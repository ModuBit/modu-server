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

import hashlib
import os
import time
from typing import AsyncGenerator, BinaryIO, Generator
from urllib.parse import quote_plus

import aiofiles
import aiofiles.os
from config import app_config
from loguru import logger
from utils import file_utils
from utils.crypto import composition

from .storage import Storage


class LocalFsStorage(Storage):
    """
    本地文件系统存储
    """

    def __init__(self, root_path: str):
        self._bucket = root_path
        self._root_folder = "storage"
        logger.info("=== create local fs storage ({}) {} ===", id(self), root_path)

    def _get_file_path(self, file_key: str) -> str:
        return os.path.join(self._bucket, file_key.lstrip(os.sep))

    async def put_file(self, filename: str, data: bytes | str | BinaryIO) -> str:
        file_key = self._wrapper_date_folder(filename, self._root_folder)
        file_path = self._get_file_path(file_key)

        file_folder = os.path.dirname(file_path)
        await aiofiles.os.makedirs(file_folder, exist_ok=True)

        async with aiofiles.open(file_path, mode="wb") as f:
            if isinstance(data, (bytes, str)):
                await f.write(data.encode() if isinstance(data, str) else data)
            else:
                # 使用块读取方式处理文件对象，避免一次性加载到内存
                chunk_size = 64 * 1024  # 64KB 缓冲区
                while chunk := data.read(chunk_size):
                    await f.write(chunk)
        return file_key

    async def get_file_bytes(self, file_key: str) -> bytes:
        file_path = self._get_file_path(file_key)
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")

        async with aiofiles.open(file_path, mode="rb") as f:
            data = await f.read()
        return data

    async def get_stream(self, file_key: str) -> AsyncGenerator[bytes, None]:
        file_path = self._get_file_path(file_key)
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")

        async with aiofiles.open(file_path, mode="rb") as f:
            while chunk := await f.read(4096):  # Read in chunks of 4KB
                yield chunk

    async def delete_file(self, file_key: str) -> bool:
        file_path = self._get_file_path(file_key)
        if await aiofiles.os.path.exists(file_path):
            await aiofiles.os.remove(file_path)
        return True

    async def exists_file(self, file_key: str) -> bool:
        file_path = self._get_file_path(file_key)
        return await aiofiles.os.path.exists(file_path)

    async def sign_url(self, file_key: str, expires: int) -> str:
        real_expires, signature = file_utils.file_signature(file_key, expires)
        return f"/api/file/{quote_plus(file_key)}?expires={real_expires}&signature={signature}"
