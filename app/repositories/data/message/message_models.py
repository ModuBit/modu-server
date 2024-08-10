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

from typing import Literal, Any

from pydantic import BaseModel


class MessageBlock(BaseModel):
    """
    消息块
    """

    type: Literal["question", "answer"]
    """
    消息类型
    - question 提问
    - answer 回答
    """

    content_type: Literal["text", "refer:text"]
    """
    消息内容的类型
    - text 文本
    - refer:text 引用文本
    """

    content: str | dict
    """消息内容"""

    section_id: str
    """该部分内容ID"""


class MessageEvent(BaseModel):
    """
    消息事件
    """

    conversation_id: str
    """会话ID"""

    sender_id: str
    """发送者ID"""

    sender_role: Literal["user", "assistant"]
    """发送者角色"""

    message_id: str
    """消息ID"""

    message_time: int
    """消息时间戳"""

    message: MessageBlock
    """消息内容"""

    is_finished: bool
    """消息是否结束"""


class MessageContent(BaseModel):
    """
    消息内容
    """

    sender_id: str
    """发送者ID"""

    sender_role: Literal["user", "assistant"]
    """发送者角色"""

    message_id: str
    """消息ID"""

    message_time: int
    """消息时间戳"""

    messages: list[MessageBlock]
    """消息内容"""
