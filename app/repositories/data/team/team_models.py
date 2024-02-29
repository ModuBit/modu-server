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


class Team(BaseModel):
    """
    团队
    """

    uid: str | None = None
    """团队ID"""
    creator_uid: str
    """创建人"""
    name: str
    """团队名称"""
    description: str | None = None
    """团队简介"""
    is_personal: bool
    """是否个人团队"""
    iv: bytes | None = None
    """初始向量"""
    is_deleted: bool = Field(default=False)
    """是否删除"""


class TeamMemberStatus(str, enum.Enum):
    """
    团队成员状态
    """

    PENDING = 'pending'
    """待确认"""
    ACTIVE = 'active'
    """已激活"""
    CLOSED = 'closed'
    """已注销"""


class TeamMemberRole(str, enum.Enum):
    """
    团队成员角色
    """

    OWNER = 'owner'
    """owner"""
    ADMIN = 'admin'
    """管理员"""
    MEMBER = 'member'
    """成员"""


class TeamMembership(BaseModel):
    """
    团队成员
    """

    team_uid: str
    """团队ID"""
    member_uid: str
    """成员ID"""
    member_role: TeamMemberRole
    """成员角色"""
    member_status: TeamMemberStatus
    """成员状态"""
