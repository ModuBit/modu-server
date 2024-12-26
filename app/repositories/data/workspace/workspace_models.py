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

from pydantic import BaseModel, Field

from utils.pydantic import default_model_config


class WorkspaceType(str, enum.Enum):
    """
    空间类型
    """

    PRIVATE = "PRIVATE"
    """私有空间"""
    PUBLIC = "PUBLIC"
    """公开空间"""


class Workspace(BaseModel):
    """
    空间
    """

    uid: str | None = None
    """空间ID"""
    creator_uid: str
    """创建人"""
    name: str
    """空间名称"""
    description: str | None = None
    """空间简介"""
    type: WorkspaceType
    """空间类型"""
    is_deleted: bool = Field(default=False)
    """是否删除"""

    # 定义配置
    model_config = default_model_config({"extra": "allow"})


class WorkspaceMemberStatus(str, enum.Enum):
    """
    空间成员状态
    """

    PENDING = "PENDING"
    """待确认"""
    ACTIVE = "ACTIVE"
    """已激活"""
    CLOSED = "CLOSED"
    """已注销"""


class WorkspaceMemberRole(str, enum.Enum):
    """
    空间成员角色
    """

    OWNER = "OWNER"
    """owner"""
    ADMIN = "ADMIN"
    """管理员"""
    MEMBER = "MEMBER"
    """成员"""


class WorkspaceMembership(BaseModel):
    """
    空间成员
    """

    workspace_uid: str
    """空间ID"""

    member_uid: str
    """成员ID"""

    member_role: WorkspaceMemberRole
    """成员角色"""

    member_status: WorkspaceMemberStatus
    """成员状态"""

    # 定义配置
    model_config = default_model_config()
