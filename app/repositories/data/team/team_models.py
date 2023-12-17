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
from dataclasses import dataclass

from utils.dataclass import tolerant


@tolerant
@dataclass
class Team:
    """
    团队
    """

    # 团队ID
    uid: str
    # 创建人
    creator_uid: str
    # 团队名称
    name: str
    # 团队简介
    description: str | None
    # 是否个人团队
    is_personal: bool
    # 是否删除
    is_deleted: bool


class TeamMemberStatus(str, enum.Enum):
    """
    团队成员状态
    """

    # 待确认
    PENDING = 'pending'
    # 已激活
    ACTIVE = 'active'
    # 已注销
    CLOSED = 'closed'


class TeamMemberRole(str, enum.Enum):
    """
    团队成员角色
    """

    # owner
    OWNER = 'owner'
    # 管理员
    ADMIN = 'admin'
    # 成员
    MEMBER = 'member'


@tolerant
@dataclass
class TeamMembership:
    """
    团队成员
    """

    # 团队ID
    team_uid: str
    # 成员ID
    member_uid: str
    # 成员角色
    member_role: TeamMemberRole
    # 成员状态
    member_status: TeamMemberStatus
