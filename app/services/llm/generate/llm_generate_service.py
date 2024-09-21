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
from typing import AsyncIterator

from boltons.strutils import multi_replace
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.schema import StreamEvent
from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.graph.graph import CompiledGraph
from loguru import logger
from pydantic import BaseModel
from starlette.responses import ContentStream
from ulid import ULID

from llm.model import model_provider_factory
from llm.model.entities.model import ModelType
from llm.model.entities.models import TextGenerationModel
from repositories.data import conversation_repository, message_repository
from repositories.data.account.account_models import Account
from repositories.data.database import BasePO
from repositories.data.message.conversation_models import Conversation
from repositories.data.message.message_models import MessageBlock, MessageEventData, Message
from services.llm import llm_model_service, llm_provider_service
from services.llm.generate.llm_message_checkpoint import LLMMessageCheckPointSaver
from services.llm.generate.llm_message_event_models import MessageStartEvent, MessageEndEvent, ErrorEvent, MessageEvent, \
    AIMessageChunkEvent
from services.llm.generate.llm_message_memory import ConversationSummaryBufferMemory
from utils.dictionary import dict_merge
from utils.errors.base_error import UnauthorizedError
from utils.errors.llm_error import LLMExistsError
from utils.iterator import single_element_async_iterator, merge_async_iterators
from utils.pydantic import default_model_config


class Item(BaseModel):
    type: str
    """类型"""

    content: str | dict
    """内容"""

    # 设置允许额外字段
    # 定义配置
    model_config = default_model_config({"extra": "allow"})


class Query(BaseModel):
    inputs: list[Item]
    """输入的内容"""

    refers: list[Item] = []
    """引用的内容"""

    # 定义配置
    model_config = default_model_config()


class GenerateCmd(BaseModel):
    conversation_uid: str | None = None
    """会话ID"""

    query: Query
    """会话内容"""

    mentions: list[str] = []
    """@的机器人"""

    # 定义配置
    model_config = default_model_config()


async def clear_memory(current_user: Account, conversation_uid: str) -> list[Message]:
    # TODO 这里需要考虑加锁

    # 找到会话
    conversation = await conversation_repository.get_by_uid(current_user.uid, conversation_uid)
    if not conversation:
        raise UnauthorizedError('找不到当前会话')

    # 找到最后一条消息
    latest_message = await message_repository.find_latest(conversation_uid, 1,
                                                          reset_message_uid=conversation.reset_message_uid)
    latest_message = latest_message[-1] if latest_message else None

    if not latest_message or latest_message.message_uid == conversation.reset_message_uid:
        # 还没有消息，或者 最后一条消息就是重置消息
        # 防止重复重置
        return []

    # 保存消息
    reset_message = Message(
        conversation_uid=conversation_uid,
        sender_uid="system",
        sender_role="system",
        messages=[MessageBlock(
            type="system",
            content_type="text",
            content="以下为新对话",
            section_uid=BasePO.uid_generate())
        ],
        message_time=int(datetime.now().timestamp()) * 1000
    )
    reset_message = await message_repository.add(reset_message)

    # 更新会话
    await conversation_repository.update_reset_message_uid(conversation_uid, reset_message.message_uid)

    return [reset_message]


async def generate(current_user: Account, workspace_uid: str, chat_generate_cmd: GenerateCmd) -> dict | ContentStream:
    """
    生成对话
    :param current_user: 当前用户
    :param workspace_uid: 空间ID
    :param chat_generate_cmd: 会话指令
    :return: 会话流
    """

    # 初始化 conversation
    first_text_message = next(filter(lambda item: item.type == "text", chat_generate_cmd.query.inputs)).content
    conversation_name = multi_replace(first_text_message, {'\n': ' '})[:30] if first_text_message else "对话"
    conversation = Conversation(conversation_uid=chat_generate_cmd.conversation_uid or "",
                                creator_uid=current_user.uid, name=conversation_name)
    conversation = await _init_generate_conversation(current_user, conversation)

    # 历史会话
    memory = ConversationSummaryBufferMemory(
        current_user=current_user,
        workspace_uid=workspace_uid,
        conversation=conversation
    )
    summary_buffer_messages = await memory.get_summary_buffer_messages(to_langchain=True)

    # 存储 user message
    question_messages = ([MessageBlock(type="question",
                                       content_type=f'refer:{_refer.type}',
                                       content=_refer.content,
                                       section_uid=BasePO.uid_generate()) for _refer in
                          chat_generate_cmd.query.refers] +
                         [MessageBlock(type="question",
                                       content_type=_input.type,
                                       content=_input.content,
                                       section_uid=BasePO.uid_generate()) for _input in chat_generate_cmd.query.inputs]
                         )
    user_message = Message(
        conversation_uid=conversation.conversation_uid,
        sender_uid=current_user.uid,
        sender_role="user",
        messages=question_messages,
        message_time=int(datetime.now().timestamp()) * 1000)
    await message_repository.add(user_message)

    # 编译机器人
    chat_bot = await _make_graph_bot(current_user, workspace_uid, chat_generate_cmd)

    # 机器人对话
    llm_event_stream = chat_bot.astream_events(
        {"messages": summary_buffer_messages + [HumanMessage(content=first_text_message)]},
        {"configurable": {"thread_id": "1"}}, version="v2")

    # 前置内容
    before_events = single_element_async_iterator(MessageStartEvent(section_uid=str(ULID())))

    # 生成内容
    llm_message_events = llm_stream_events(llm_event_stream)

    # 后置内容
    after_events = single_element_async_iterator(MessageEndEvent(section_uid=str(ULID())))

    # 合并内容
    message_events = merge_async_iterators(
        before_events, llm_message_events, after_events,
        yield_when_exception=lambda e: ErrorEvent(section_uid=str(ULID()), error=e))

    return message_events_checkpoint(current_user, workspace_uid, message_events, conversation, "")


async def _make_graph_bot(current_user: Account, workspace_uid: str, chat_generate_cmd: GenerateCmd) -> CompiledGraph:
    """
    TODO 仅用于演示，需要重新设计
    """

    system_models = await llm_model_service.get_system_config(current_user, workspace_uid)
    if not system_models or ModelType.TEXT_GENERATION not in system_models:
        raise LLMExistsError(
            message='您还没有配置系统推理模型，请在 空间-设置-模型-系统模型设置 中添加 系统推理模型')

    # model 配置
    model_config = system_models[ModelType.TEXT_GENERATION]

    # provider 配置
    provider_config = await llm_provider_service.detail(current_user, workspace_uid, model_config.provider_name)
    provider_config.decrypt_credential()

    # provider → model → chat_model
    provider = model_provider_factory.get_provider(model_config.provider_name)
    model: TextGenerationModel = provider.get_model(ModelType.TEXT_GENERATION)
    chat_model: BaseChatModel = model.chat_model(provider_credential=provider_config.provider_credential,
                                                 model_parameters=model_config.model_parameters,
                                                 model_name=model_config.model_name,
                                                 streaming=True,
                                                 request_timeout=5,
                                                 max_retries=0) if model else None

    if not chat_model:
        raise LLMExistsError(message=f'您在{model_config.provider_name}中还未配置任何{ModelType.TEXT_GENERATION}模型')

    async def chat(state: MessagesState, config: RunnableConfig):
        system_message = SystemMessage(content="你是墨读助理，由墨读科技(MODU)创建，旨在帮助用户使用墨读产品。"
                                               "墨读是一款AI聊天机器人开发平台，它允许用户通过直观的拖放界面和丰富的插件库来快速构建、调试和优化AI聊天机器人，而无需具备专业的编程知识。"
                                               "用户可以根据自己的需求定制聊天机器人的功能，例如用于寻找热点信息、撰写报告或是规划旅行等。"
                                               "墨读产品官网是https://modu.manerfan.com，项目开源地址https://github.com/modubit。")
        messages = state["messages"] or []
        if messages and isinstance(messages[0], SystemMessage):
            system_message = SystemMessage(content=f'{system_message.content}\n\n{messages[0].content}')
            messages = messages[1:]
        response = await chat_model.ainvoke([system_message] + messages,
                                            dict_merge(config, {'tags': ['explain_tag']}))
        return {"messages": response}

    workflow = StateGraph(MessagesState)
    workflow.add_node("chat", chat)
    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", END)

    return workflow.compile()


async def _init_generate_records(conversation: Conversation, user_message: Message) -> (str, str):
    """
    初始化会话消息
    :param conversation: 当前用户
    :param user_message: 会话内容
    :return: (conversation_uid, message_uid)
    """

    conversation_uid = conversation.conversation_uid
    if not conversation_repository.get_by_uid(conversation_uid):
        _conversation = await conversation_repository.create(conversation)
        conversation_uid = _conversation.conversation_uid

    user_message.conversation_uid = conversation_uid
    await message_repository.add(user_message)

    # 生成新的 message_uid 给 assistant 使用
    return conversation_uid, BasePO.uid_generate()


async def _init_generate_conversation(current_user: Account, conversation: Conversation) -> Conversation:
    """
    初始化会话
    :param conversation: 当前用户
    :return: Conversation
    """

    if conversation.conversation_uid:
        conversation = await conversation_repository.get_by_uid(current_user.uid, conversation.conversation_uid)

    if not conversation or not conversation.conversation_uid:
        conversation = await conversation_repository.create(conversation)

    return conversation


async def llm_stream_events(event_iter: AsyncIterator[StreamEvent]) -> AsyncIterator[MessageEvent]:
    """
    通常，langgraph使用 BaseCheckpointSaver 处理历史消息
    langgraph.graph.state.StateGraph.compile(checkpoint=)
    https://langchain-ai.github.io/langgraph/how-tos/persistence/

    由于对历史消息的处理和端的展示高度耦合，同时对历史消息有定制化的诉求，langgraph的CheckpointSaver无法满足
    这里需要自定义处理逻辑

    :param event_iter: 异步事件流
    :return: 处理后的 异步事件流
    """

    section_uid = str(ULID())
    try:
        async for event in event_iter:
            logger.debug(event)
            if event['event'] == 'on_chat_model_stream':
                chunk_event = AIMessageChunkEvent(section_uid=section_uid, chunk=event['data']['chunk'])
                yield chunk_event
            # TODO 其他类型判断
    except Exception as e:
        logger.exception(f"invoke llm stream error: {str(e)}")
        yield ErrorEvent(section_uid=str(ULID()), error=e)


async def message_events_checkpoint(current_user: Account, workspace_uid: str,
                                    event_iter: AsyncIterator[MessageEvent],
                                    conversation: Conversation, assistant_uid: str):
    checkpoint_saver = LLMMessageCheckPointSaver(
        current_user=current_user,
        workspace_uid=workspace_uid,
        conversation=conversation,
        assistant_uid=assistant_uid
    )

    message_uid = BasePO.uid_generate()

    async for event in event_iter:
        if isinstance(event, MessageStartEvent):
            message = MessageEventData(
                conversation_uid=conversation.conversation_uid,
                sender_uid=assistant_uid,
                sender_role="assistant",
                message_uid=message_uid,
                message_time=int(datetime.now().timestamp()) * 1000,
                message=MessageBlock(
                    type="answer",
                    content_type="text",
                    content="",
                    section_uid=event.section_uid,
                ),
                is_finished=False,
            )
            yield f'event: message\ndata: {message.model_dump_json(by_alias=True)}\n\n'

        if isinstance(event, AIMessageChunkEvent):
            message = MessageEventData(
                conversation_uid=conversation.conversation_uid,
                sender_uid=assistant_uid,
                sender_role="assistant",
                message_uid=message_uid,
                message_time=int(datetime.now().timestamp()) * 1000,
                message=MessageBlock(
                    type="answer",
                    content_type="text",
                    content=event.chunk.content,
                    section_uid=event.section_uid,
                ),
                is_finished=False,
            )
            checkpoint_saver.process(message)
            yield f'event: message\ndata: {message.model_dump_json(by_alias=True)}\n\n'

        if isinstance(event, MessageEndEvent):
            await checkpoint_saver.save()
            yield f'event: done\n\n'

        if isinstance(event, ErrorEvent):
            message = MessageEventData(
                conversation_uid=conversation.conversation_uid,
                sender_uid=assistant_uid,
                sender_role="assistant",
                message_uid=message_uid,
                message_time=int(datetime.now().timestamp()) * 1000,
                message=MessageBlock(
                    type="answer",
                    content_type="error",
                    content=str(event.error),
                    section_uid=event.section_uid,
                ),
                is_finished=True,
            )
            checkpoint_saver.process(message)
            await checkpoint_saver.save()
            yield f'event: error\ndata: {message.model_dump_json(by_alias=True)}\n\n'
