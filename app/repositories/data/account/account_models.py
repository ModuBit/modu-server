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

from pydantic import BaseModel


class AccountStatus(str, enum.Enum):
    """
    用户状态
    """

    PENDING = 'PENDING'
    """待激活"""
    ACTIVE = 'ACTIVE'
    """已激活"""
    BANNED = 'BANNED'
    """已禁用"""
    CLOSED = 'CLOSED'
    """已注销"""


class Account(BaseModel):
    """
    账号
    """

    uid: str | None = None
    """账号ID"""
    name: str
    """账号名称"""
    email: str
    """账号邮箱"""
    password: str | None = None
    """账号密码"""
    avatar: str | None = None
    """账号头像"""
    status: AccountStatus
    """账号状态"""
