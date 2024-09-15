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

import asyncio
import itertools

from langchain.chains.llm import LLMChain
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, get_buffer_string

from llm.model import model_provider_factory
from llm.model.entities.model import ModelType
from llm.model.entities.models import TextGenerationModel
from repositories.data import message_repository, message_summary_repository
from repositories.data.account.account_models import Account
from repositories.data.message.message_models import Message, MessageBlock, MessageSummary
from services.llm import llm_model_service, llm_provider_service
from services.llm.generate.prompt import SUMMARY_PROMPT
from utils.errors.llm_error import LLMExistsError


class ConversationSummaryBufferMemory:
    def __init__(self, current_user: Account, workspace_uid: str, conversation_uid: str):
        self._current_user = current_user
        self._workspace_uid = workspace_uid
        self._conversation_uid = conversation_uid

    async def save_messages(self, messages: list[Message], prune_exec_background: bool = False):
        """
        向会话中添加消息，如果历史消息过长，则对消息进行总结
        :param messages: 消息
        :param prune_exec_background: 是否在后台执行消息总结
        """
        for message in messages:
            message.conversation_uid = self._conversation_uid

        await message_repository.add_batch(messages)

        if prune_exec_background:
            asyncio.create_task(self._prune())
        else:
            await self._prune()

    async def _prune(self):
        """
        对消息进行总结
        """
        message_summary = await message_summary_repository.get_latest(self._conversation_uid)
        summary, summary_latest_message_uid = \
            (message_summary.summary, message_summary.last_message_uid) if message_summary else (None, None)

        # 待总结的消息数
        messages_count_waiting_summary = await message_repository.count_after_uid(self._conversation_uid,
                                                                                  summary_latest_message_uid)
        # 待总结的消息数小于10，则不进行总结
        if messages_count_waiting_summary < 10:
            return

        # 待总结的消息
        messages_waiting_summary = await message_repository.find_all_after_uid(self._conversation_uid,
                                                                               summary_latest_message_uid, 10)
        if not messages_waiting_summary:
            return

        # 转换成 langchain BaseMessage
        base_messages_waiting_summary = [
            ConversationSummaryBufferMemory._message_to_base_message(message_waiting_summary)
            for message_waiting_summary in messages_waiting_summary]
        base_messages_waiting_summary = list(itertools.chain.from_iterable(base_messages_waiting_summary))

        # 转换成 prompt 中可识别的内容
        new_messages = get_buffer_string(base_messages_waiting_summary)

        # 使用 系统设置中的 文本生成模型 生成新的总结
        chat_model = await self._system_chat_model()
        chain = LLMChain(llm=chat_model, prompt=SUMMARY_PROMPT)
        new_summary = await chain.apredict(summary=summary, new_lines=new_messages)

        # 保存总结
        await message_summary_repository.add(MessageSummary(conversation_uid=self._conversation_uid,
                                                            summary=new_summary,
                                                            last_message_uid=messages_waiting_summary[-1].message_uid))

    async def _system_chat_model(self) -> BaseChatModel:
        system_models = await llm_model_service.get_system_config(self._current_user, self._workspace_uid)
        if not system_models or ModelType.TEXT_GENERATION not in system_models:
            raise LLMExistsError(
                message='您还没有配置系统推理模型，请在 空间-设置-模型-系统模型设置 中添加 系统推理模型')

        # model 配置
        model_config = system_models[ModelType.TEXT_GENERATION]

        # provider 配置
        provider_config = await llm_provider_service.detail(self._current_user, self._workspace_uid,
                                                            model_config.provider_name)
        provider_config.decrypt_credential()

        # provider → model → chat_model
        provider = model_provider_factory.get_provider(model_config.provider_name)
        model: TextGenerationModel = provider.get_model(ModelType.TEXT_GENERATION)
        return model.chat_model(provider_credential=provider_config.provider_credential,
                                model_parameters=model_config.model_parameters,
                                model_name=model_config.model_name,
                                streaming=True,
                                request_timeout=5,
                                max_retries=0) if model else None

    @staticmethod
    def _message_to_base_message(message: Message) -> list[BaseMessage]:
        """
        把存储的消息转为langchain 兼容的消息类型
        :param message: 存储的消息
        """
        if message.sender_role == "user":
            contents = [ConversationSummaryBufferMemory._message_block_content(block) for block in message.messages]
            contents = list(filter(lambda x: x is not None, contents))
            return [HumanMessage(content=contents)]
        if message.sender_role == "assistant":
            contents = [ConversationSummaryBufferMemory._message_block_content(block) for block in message.messages]
            contents = list(filter(lambda x: x is not None, contents))
            return [AIMessage(content=content) for content in contents]

        # TODO 其他类型的支持
        return []

    @staticmethod
    def _message_block_content(message_block: MessageBlock):
        if "text" in message_block.content_type:
            return message_block.content

        # TODO 其他类型的支持
        return None
