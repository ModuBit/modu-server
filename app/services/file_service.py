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

from typing import AsyncGenerator, Tuple
from urllib.parse import unquote_plus
from config import app_config
from fastapi import UploadFile
from repositories.data import file_repository
from repositories.data.account.account_models import Account
from repositories.data.file.file_models import File
from repositories.storage import get_storage, storage
from ulid import ULID
from utils import file_utils


async def file_upload(current_user: Account, file: UploadFile) -> File:
    """
    文件上传
    :param file: 文件
    :return: 文件
    """

    # 支持的文件类型及限制
    support_file_types = app_config.repository.storage.support_file_types
    match_support_file_type = None

    # 验证文件类型及大小
    for support_file_type in support_file_types:
        if file_utils.validate_file_type(
            file.content_type, file.filename, support_file_type.accept
        ):
            match_support_file_type = support_file_type
            max_size = file_utils.get_number_from_string(support_file_type.max_size)
            if max_size and file.size > max_size:
                raise ValueError(
                    f"文件大小不能超过{file_utils.readable_size(max_size)}"
                )
            break

    # 未匹配到支持的文件类型
    if not match_support_file_type:
        raise ValueError(f"不支持该文件类型")

    # 获取文件后缀
    _, file_ext = file_utils.get_file_name_and_ext(file.filename)
    # 计算文件hash
    file_hash = file_utils.file_hash(file.file)

    # 上传文件
    file_key = await storage.put_file(".".join([str(ULID()), file_ext]), file.file)

    # 保存文件信息
    file_info = await file_repository.create_file(
        File(
            file_key=file_key,
            filename=file.filename,
            file_mime_type=file.content_type,
            file_category=match_support_file_type.type,
            file_size=file.size,
            file_hash=file_hash,
            storage_type=app_config.repository.storage.type,
            creator_uid=current_user.uid,
        )
    )

    # 预览地址
    file_url = await get_file_url(file_info)
    file_info.file_url = file_url
    return file_info


async def get_file_url_by_uid(file_uid: str) -> str:
    """
    文件URL
    :param file_uid: 文件uid
    :return: 文件URL
    """
    file = await file_repository.get_file_by_uid(file_uid)
    return await get_file_url(file)


async def get_file_url_by_key(file_key: str) -> str | None:
    """
    文件URL
    :param file_key: 文件key
    :return: 文件URL
    """
    file = await file_repository.get_file_by_key(file_key)
    return await get_file_url(file)


async def get_file_url(file: File | None) -> str | None:
    """
    文件URL
    :param file: 文件
    :return: 文件URL
    """
    if not file:
        return None

    _storage = get_storage(file.storage_type)
    return await _storage.sign_url(file.file_key, 7 * 24 * 3600) if _storage else None


async def file_content(file_key: str, expires: int, signature: str) -> Tuple[AsyncGenerator[bytes, None], File]:
    """
    文件内容
    :param file_key: 文件KEY
    :param expires: 过期时间
    :param signature: 签名
    :return: 文件流, 文件
    """
    file_key = unquote_plus(file_key)

    # 验证签名
    file_utils.file_signature_check(file_key, expires, signature)

    # 获取文件
    file = await file_repository.get_file_by_key(file_key)

    # 获取文件流
    _storage = get_storage(file.storage_type)
    file_stream = _storage.get_stream(file_key)

    return file_stream, file
