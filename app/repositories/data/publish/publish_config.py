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

import enum
from datetime import datetime

from pydantic import BaseModel


class PublishConfigTargetType(str, enum.Enum):
    """
    配置发布目标类型
    """

    BOT_CONFIG = "BOT_CONFIG"


class PublishConfigStatus(str, enum.Enum):
    """
    配置发布状态
    """

    DRAFT = "DRAFT"
    """草稿"""
    PUBLISHED = "PUBLISHED"
    """已发布"""


class PublishConfig(BaseModel):
    """
    配置发布
    """

    uid: str | None = None
    """UID"""
    created_at: datetime | None = None
    """创建时间"""
    target_type: PublishConfigTargetType
    """目标类型"""
    target_uid: str
    """目标uid"""
    config_mode: str
    """配置模式"""
    config_content: dict
    """配置内容"""
    publish_status: PublishConfigStatus
    """发布状态"""
