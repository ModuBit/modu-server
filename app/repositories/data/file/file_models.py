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

from pydantic import BaseModel

from utils.pydantic import default_model_config

class SimpleFile(BaseModel):
    """
    简单文件
    """

    file_key: str
    """文件KEY"""

    filename: str
    """文件名"""

    # 定义配置
    model_config = default_model_config({"extra": "allow"})


class File(BaseModel):
    """
    文件
    """

    file_key: str
    """文件KEY"""

    filename: str
    """文件名"""

    file_mime_type: str
    """文件MIME类型"""

    file_category: str
    """文件分类"""

    file_size: int
    """文件大小"""

    file_hash: str
    """文件哈希"""

    storage_type: str
    """存储类型"""

    creator_uid: str
    """创建者uid"""

    # 定义配置
    model_config = default_model_config({"extra": "allow"})
