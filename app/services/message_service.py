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
from typing import AsyncIterator, Tuple

from langchain_core.runnables.schema import StreamEvent
from loguru import logger
from ulid import ULID

from repositories.data.message.message_models import MessageEvent, MessageBlock


async def stream_event_checkpoint(event_iter: AsyncIterator[StreamEvent],
                                  conversation_id: str | None = None) -> Tuple[AsyncIterator[str], str, str]:
    """
    通常，langgraph使用 BaseCheckpointSaver 处理历史消息
    langgraph.graph.state.StateGraph.compile(checkpoint=)
    https://langchain-ai.github.io/langgraph/how-tos/persistence/

    由于对历史消息的处理和端的展示高度耦合，同时对历史消息有定制化的诉求，langgraph的CheckpointSaver无法满足
    这里需要自定义处理逻辑

    :param event_iter: 异步事件流
    :param conversation_id: 会话 ID
    :return: 处理后的、可供端直接使用的 异步消息流
    """

    thread_id = conversation_id or str(ULID())
    message_id = str(ULID())

    message_iter = _stream_event_checkpoint(event_iter, thread_id, message_id)

    return message_iter, thread_id, message_id


async def _stream_event_checkpoint(event_iter: AsyncIterator[StreamEvent],
                                   conversation_id: str, message_id: str) -> AsyncIterator[str]:
    """
    通常，langgraph使用 BaseCheckpointSaver 处理历史消息
    langgraph.graph.state.StateGraph.compile(checkpoint=)
    https://langchain-ai.github.io/langgraph/how-tos/persistence/

    由于


    :param event_iter: 异步事件流
    :return: 处理后的、可供端直接使用的 异步消息流
    """

    section_id = str(ULID())

    async for event in event_iter:
        logger.debug(event)
        if event['event'] == 'on_chat_model_stream':
            message = MessageEvent(
                conversation_id=conversation_id,
                sender_id="",
                sender_role="assistant",
                message_id=message_id,
                message_time=int(datetime.now().timestamp()),
                message=MessageBlock(
                    type="answer",
                    content_type="text",
                    content=event["data"]["chunk"].content,
                    section_id=section_id,
                ),
                is_finished=False,
            )
            yield f'id: {datetime.now()}\nevent: message\ndata: {message.json()}\n\n'

    message = MessageEvent(
        conversation_id=conversation_id,
        sender_id="",
        sender_role="assistant",
        message_id=message_id,
        message_time=int(datetime.now().timestamp()),
        message=MessageBlock(
            type="answer",
            content_type="text",
            content="",
            section_id=section_id,
        ),
        is_finished=True,

    )
    yield f'id: {datetime.now()}\nevent: message\ndata: {message.json()}\n\n'
