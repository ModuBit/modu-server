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

from repositories.data.account.account_models import Account
from repositories.data.message.message_models import Message, MessageEventData
from services.llm.generate.llm_message_memory import ConversationSummaryBufferMemory


class LLMMessageCheckPointSaver:
    """
    通常，langgraph使用 BaseCheckpointSaver 处理历史消息
    langgraph.graph.state.StateGraph.compile(checkpoint=)
    https://langchain-ai.github.io/langgraph/how-tos/persistence/

    由于对历史消息的处理和端的展示高度耦合，同时对历史消息有定制化的诉求，langgraph的CheckpointSaver无法满足
    这里需要自定义处理逻辑
    """

    def __init__(self, current_user: Account, workspace_uid: str, conversation_uid: str, assistant_uid: str):
        """
        LLMMessageCheckPointSaver
        :param conversation_uid: 会话 UID
        :param assistant_uid: 应用/机器人 UID
        """
        self._saved: bool = False

        self._current_user = current_user
        self.workspace_uid = workspace_uid

        self._conversation_uid = conversation_uid
        self._assistant_uid = assistant_uid

        self._conversation_messages: list[Message] = []
        self._current_message: Message | None = None

        self._conversationSummaryBufferMemory = ConversationSummaryBufferMemory(
            current_user=current_user,
            workspace_uid=workspace_uid,
            conversation_uid=conversation_uid
        )

    def process(self, message_event: MessageEventData):
        """
        逐一处理消息事件，与前端保持逻辑一致 pages/Modu/Chat/index.tsx#Chat.messageParser
        :param message_event: 消息事件
        """

        if self._saved:
            # 已经保存过了
            return

        if not self._current_message or self._current_message.message_uid != message_event.message_uid:
            # 新消息
            self._current_message = Message(
                conversation_uid=self._conversation_uid,
                message_uid=message_event.message_uid,
                sender_uid=self._assistant_uid,
                sender_role="assistant",
                message_time=message_event.message_time,
                messages=[message_event.message])

            self._conversation_messages.append(self._current_message)
        else:
            # 追加消息内容
            last_section_uid = self._conversation_messages[-1].messages[-1].section_uid
            if last_section_uid != message_event.message.section_uid:
                # 新的 section
                self._conversation_messages[-1].messages.append(message_event.message)
            else:
                # 在原 section 上追加内容
                last_message_block = self._conversation_messages[-1].messages[-1]
                last_message_block.content += message_event.message.content

    async def save(self):
        """
        保存消息
        """
        await self._conversationSummaryBufferMemory.save_messages(self._conversation_messages, True)
        self._saved = True
