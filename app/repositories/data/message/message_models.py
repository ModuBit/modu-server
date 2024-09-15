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
from datetime import datetime
from typing import Literal

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

    content_type: Literal["text", "refer:text", "error"]
    """
    消息内容的类型
    - text 文本
    - refer:text 引用文本
    """

    content: str | dict
    """消息内容"""

    section_uid: str
    """该部分内容ID"""


class MessageEventData(BaseModel):
    """
    消息事件
    """

    conversation_uid: str
    """会话ID"""

    message_uid: str
    """消息ID"""

    message_time: int = int(datetime.now().timestamp()) * 1000
    """消息时间戳"""

    sender_uid: str
    """发送者UID"""

    sender_role: Literal["user", "assistant"]
    """发送者角色"""

    message: MessageBlock
    """消息内容"""

    is_finished: bool
    """消息是否结束"""


class Message(BaseModel):
    """
    消息
    """

    conversation_uid: str
    """会话ID"""

    message_uid: str = ""
    """消息ID"""

    message_time: int = int(datetime.now().timestamp()) * 1000
    """消息时间戳"""

    sender_uid: str
    """发送者UID"""

    sender_role: Literal["user", "assistant"]
    """发送者角色"""

    messages: list[MessageBlock]
    """消息内容"""

class MessageSummary(BaseModel):
    """
    消息总结
    """

    conversation_uid: str
    """会话ID"""

    summary: str
    """会话摘要总结"""

    last_message_uid: str
    """会话总结时最后一条消息uid"""
