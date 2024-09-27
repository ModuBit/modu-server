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


class Conversation(BaseModel):
    """
    会话
    """

    conversation_uid: str = ""
    """会话 uid"""

    creator_uid: str
    """创建者uid"""

    workspace_uid: str = 'ROOT'
    """空间uid"""

    name: str
    """会话名"""

    reset_message_uid: str | None = None
    """重置/清楚记忆 时的消息UID"""

    created_at: int | None = None
    """创建时间"""

    # 定义配置
    model_config = default_model_config()
