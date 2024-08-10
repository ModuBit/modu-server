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

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel, Extra
from starlette.responses import ContentStream
from ulid import ULID

from llm.model import model_provider_factory
from llm.model.entities.model import ModelType
from llm.model.entities.models import TextGenerationModel
from repositories.data.account.account_models import Account
from repositories.data.message.message_models import MessageEvent, MessageBlock
from services import workspace_service
from services.llm import llm_model_service, llm_provider_service
from services.message_service import stream_event_checkpoint
from utils.dictionary import dict_merge
from utils.errors.llm_error import LLMExistsError
from utils.errors.space_error import SpaceExistsError
from utils.iterator import single_element_async_iterator, merge_async_iterators


class Item(BaseModel):
    type: str
    """类型"""

    content: str | dict
    """内容"""

    # 设置允许额外字段
    class Config:
        extra = Extra.allow


class Query(BaseModel):
    inputs: list[Item]
    """输入的内容"""

    refers: list[Item] = []
    """引用的内容"""


class GenerateCmd(BaseModel):
    conversation_id: str | None = None
    """会话ID"""

    query: Query
    """会话内容"""

    mentions: list[str] = []
    """@的机器人"""


async def generate(current_user: Account, chat_generate_cmd: GenerateCmd) -> dict | ContentStream:
    """
    生成对话
    :param current_user: 当前用户
    :param chat_generate_cmd: 会话指令
    :return: 会话流
    """

    # 编译机器人
    chat_bot = await _make_graph_bot(current_user, chat_generate_cmd)

    # 机器人对话
    event_stream = chat_bot.astream_events({"messages": [
        HumanMessage(content=next(filter(lambda item: item.type == "text", chat_generate_cmd.query.inputs)).content)
    ]}, {"configurable": {"thread_id": "1"}}, version="v2")

    # 对话内容
    message, conversation_id, message_id = await stream_event_checkpoint(event_stream,
                                                                         chat_generate_cmd.conversation_id)

    # 前置内容
    before_message = MessageEvent(
        conversation_id=conversation_id,
        sender_id=current_user.uid,
        sender_role="assistant",
        message_id=message_id,
        message_time=int(datetime.now().timestamp()),
        message=MessageBlock(
            type="answer",
            content_type="text",
            content=f'```mermaid\n{chat_bot.get_graph().draw_mermaid()}\n```',
            section_id=str(ULID()),
        ),
        is_finished=False,
    )
    before = single_element_async_iterator(
        f'id: {datetime.now()}\nevent: message\ndata: {before_message.json()}\n\n')

    # 后置内容
    after = single_element_async_iterator(
        f'id: {datetime.now()}\nevent: done\n\n')

    # 合并内容
    return merge_async_iterators(before, message, after)


async def _make_graph_bot(current_user: Account, chat_generate_cmd: GenerateCmd) -> CompiledGraph:
    """
    TODO 仅用于演示，需要重新设计
    """

    workspace = await workspace_service.mine(current_user)
    if not workspace:
        raise SpaceExistsError(message='找不到您的个人空间，请联系管理员')

    system_models = await llm_model_service.get_system_config(current_user, workspace.uid)
    if not system_models or ModelType.TEXT_GENERATION not in system_models:
        raise LLMExistsError(
            message='您还没有配置系统推理模型，请在 个人空间-设置-模型-系统模型设置 中添加 系统推理模型')

    # model 配置
    model_config = system_models[ModelType.TEXT_GENERATION]

    # provider 配置
    provider_config = await llm_provider_service.detail(current_user, workspace.uid, model_config.provider_name)
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

    async def explain(state: MessagesState, config: RunnableConfig):
        message = state["messages"][-1]
        response = await chat_model.ainvoke([
            SystemMessage(
                content="你是文学大师，帮助用户解释文字的含义，请直接给出释义"),
            message
        ], dict_merge(config, {'tags': ['explain_tag']}))
        return {"messages": response}

    async def translate(state: MessagesState, config: RunnableConfig):
        message = state["messages"][-1]
        response = await chat_model.ainvoke([
            SystemMessage(
                content="Translate the following from Chinese into English."),
            message
        ], dict_merge(config, {'tags': ['translate_tag']}))
        return {"messages": response}

    workflow = StateGraph(MessagesState)
    workflow.add_node("explain", explain)
    workflow.add_node("translate", translate)
    workflow.add_edge(START, "explain")
    workflow.add_edge("explain", "translate")
    workflow.add_edge("translate", END)

    # langgraph.graph.state.StateGraph.compile(checkpoint=)
    # https://langchain-ai.github.io/langgraph/how-tos/persistence/
    return workflow.compile()
