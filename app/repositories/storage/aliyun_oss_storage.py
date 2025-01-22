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

from typing import AsyncGenerator, BinaryIO, Generator
import asyncio
import oss2
from loguru import logger

from .storage import Storage


class AliyunOssStorage(Storage):
    """
    阿里云OSS存储
    """

    def __init__(self, access_key_id: str, access_key_secret: str, endpoint: str, region: str, bucket_name: str):
        self._root_folder = 'storage'
        self._bucket_name = bucket_name
        self._bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name, region=region)
        logger.info("=== create aliyun oss storage ({}) {}/{} ===", id(self), endpoint, bucket_name)

    async def put_file(self, filename: str, data: bytes | str | BinaryIO) -> str:
        file_key = self._wrapper_date_folder(filename, self._root_folder)
        await asyncio.to_thread(self._bucket.put_object, file_key, data)
        return file_key
    
    async def get_file_bytes(self, file_key: str) -> bytes:
        return await asyncio.to_thread(lambda: self._bucket.get_object(file_key).read())
    
    async def get_stream(self, file_key: str) -> AsyncGenerator[bytes, None]:
        obj = await asyncio.to_thread(self._bucket.get_object, file_key)
        while True:
            chunk = await asyncio.to_thread(obj.read, 4096)
            if not chunk:
                break
            yield chunk
    
    async def delete_file(self, file_key: str) -> bool:
        await asyncio.to_thread(self._bucket.delete_object, file_key)
        return True
    
    async def exists_file(self, file_key: str) -> bool:
        return await asyncio.to_thread(self._bucket.object_exists, file_key)
    
    async def sign_url(self, file_key: str, expires: int) -> str:
        return await asyncio.to_thread(self._bucket.sign_url, 'GET', file_key, expires)
    
