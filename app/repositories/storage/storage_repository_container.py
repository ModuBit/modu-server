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

from typing import TypeVar

from config import app_config
from utils.dictionary import dict_get
from utils.lifespan import register_pre_destroy_executor

from .aliyun_oss_storage import AliyunOssStorage
from .local_fs_storage import LocalFsStorage
from .storage import Storage

_storage: dict[str, Storage] = {}
_storage_mapping = {
    "local_fs": LocalFsStorage,
    "aliyun_oss": AliyunOssStorage,
}


def get_storage(type: str | None = None) -> Storage:
    """
    根据配置中的存储类型创建并返回一个存储实例。

    :return: 存储实例
    :raises ValueError: 如果存储类型不受支持
    """

    global _storage
    global _storage_mapping

    storage_type = type or app_config.repository.storage.type
    if storage_type not in _storage_mapping:
        raise ValueError(f"Unsupported storage type: {storage_type}")

    storage = _storage.get(storage_type)
    if storage:
        return storage

    config = dict_get(app_config, f"repository.storage.{storage_type}")
    storage = _storage_mapping[storage_type](**config)
    _storage[storage_type] = storage

    register_pre_destroy_executor(storage.close)

    return storage
