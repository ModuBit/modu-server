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


class AccountStatus(str, enum.Enum):
    """
    用户状态
    """

    # 待激活
    PENDING = 'pending'
    # 已激活
    ACTIVE = 'active'
    # 已禁用
    BANNED = 'banned'
    # 已注销
    CLOSED = 'closed'


@tolerant
@dataclass
class Account:
    """
    账号
    """

    # 账号ID
    uid: str | None
    # 账号名称
    name: str
    # 账号邮箱
    email: str
    # 账号密码
    password: str | None
    # 账号头像
    avatar: str | None
    # 账号状态
    status: AccountStatus
