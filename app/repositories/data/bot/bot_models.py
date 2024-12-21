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

from repositories.data.account.account_models import AccountInfo
from utils.pydantic import default_model_config


class BotMode(str, enum.Enum):
    """
    BOT模式
    """
    SINGLE_AGENT = "SINGLE_AGENT"
    """单智能体"""
    MULTI_AGENTS = "MULTI_AGENTS"
    """多智能体"""


class Bot(BaseModel):
    """
    BOT
    """

    uid: str | None = None
    """uid"""

    workspace_uid: str
    """空间UID"""

    name: str
    """名称"""

    avatar: str | None = None
    """头像"""

    description: str | None = None
    """描述"""

    creator_uid: str
    """创建人UID"""

    creator: AccountInfo | None = None
    """创建人"""

    mode: BotMode | None = None
    """模式"""

    config: dict | None = None
    """BOT配置"""

    publish_uid: str | None = None
    """发布UID"""

    # 定义配置
    model_config = default_model_config()
