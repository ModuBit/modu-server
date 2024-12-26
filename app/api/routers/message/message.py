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

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from fastapi.responses import StreamingResponse
from loguru import logger
from starlette.responses import ContentStream

from api.dependencies.principal import current_account
from repositories.data.account.account_models import Account
from repositories.data.message.conversation_models import Conversation
from repositories.data.message.message_models import Message
from services import llm_generate_service, workspace_service, message_service
from services.llm.generate.llm_generate_service import GenerateCmd
from utils.errors.base_error import UnauthorizedError

router = APIRouter()


def compact_async_generate_response(response: dict | ContentStream) -> Response:
    if isinstance(response, dict):
        return JSONResponse(content=response)
    return StreamingResponse(
        response,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked",
            "X-Accel-Buffering": "no",
            "Content-Encoding": "identity",
        },
    )


@logger.catch()
@router.post(path="/chat")
async def chat(
    workspace_uid: str | None,
    chat_generate_cmd: GenerateCmd,
    current_user: Account = Depends(current_account),
):
    if not workspace_uid:
        mine_workspace = await workspace_service.mine(current_user)
        if not mine_workspace:
            raise UnauthorizedError("找不到您的个人空间，请联系管理员")
        workspace_uid = mine_workspace.uid
    else:
        member_role = await workspace_service.member_role(current_user, workspace_uid)
        if member_role is None:
            raise UnauthorizedError("您无该使用该空间")

    generator = await llm_generate_service.generate(
        current_user, workspace_uid, chat_generate_cmd
    )
    response = compact_async_generate_response(generator)
    return response


@logger.catch()
@router.put(path="/chat/{conversation_uid}/stop")
async def chat(
    conversation_uid: str, current_user: Account = Depends(current_account)
) -> bool:
    """
    停止生成
    :param conversation_uid: 会话 ID
    :param current_user: 当前用户
    """
    return await llm_generate_service.stop_generate(current_user, conversation_uid)


@logger.catch()
@router.post(path="/chat/{conversation_uid}/message/clear")
async def clear_memory(
    conversation_uid: str, current_user: Account = Depends(current_account)
) -> list[Message]:
    """
    清除会话记忆
    :param conversation_uid: 会话ID
    :param current_user: 当前用户
    """
    return await llm_generate_service.clear_memory(current_user, conversation_uid)


@logger.catch()
@router.get(path="/chat/{conversation_uid}/messages")
async def messages(
    conversation_uid: str,
    before_message_uid: Optional[str] = Query(None),
    max_count: int = Query(...),
    current_user: Account = Depends(current_account),
) -> list[Message]:
    """
    查询会话消息
    :param conversation_uid: 会话 ID
    :param before_message_uid: 查询该消息之前的
    :param max_count: 返回多少条
    :param current_user: 当前用户
    """
    return await message_service.messages(
        current_user, conversation_uid, before_message_uid, max_count
    )


@logger.catch()
@router.get(path="/chat/conversations")
async def conversations(
    before_conversation_uid: Optional[str] = Query(None),
    max_count: int = Query(...),
    current_user: Account = Depends(current_account),
) -> list[Conversation]:
    """
    查询会话
    :param before_conversation_uid: 查询该会话之前的
    :param max_count: 返回多少条
    :param current_user: 当前用户
    """
    return await message_service.conversations(
        current_user, before_conversation_uid, max_count
    )


@logger.catch()
@router.get(path="/chat/conversation/latest")
async def latest_conversation(
    current_user: Account = Depends(current_account),
) -> Conversation:
    """
    查询最新会话
    :param current_user: 当前用户
    """
    return await message_service.latest_conversations(current_user)


@logger.catch()
@router.delete(path="/chat/conversation/all")
async def delete_all_conversations(
    current_user: Account = Depends(current_account),
) -> bool:
    """
    删除所有会话
    :param current_user: 当前用户
    """
    return await message_service.delete_all_conversations(current_user)


@logger.catch()
@router.delete(path="/chat/conversation/{conversation_uid}")
async def delete_conversation(
    conversation_uid: str, current_user: Account = Depends(current_account)
) -> bool:
    """
    删除会话
    :param conversation_uid: 会话 ID
    :param current_user: 当前用户
    """
    return await message_service.delete_conversation(current_user, conversation_uid)


@logger.catch()
@router.put(path="/chat/conversation/{conversation_uid}/rename")
async def rename_conversation(
    conversation_uid: str, name: str, current_user: Account = Depends(current_account)
) -> str:
    """
    修改会话名
    :param conversation_uid: 会话 ID
    :param name: 会话名
    :param current_user: 当前用户
    """
    return await message_service.rename_conversation(
        current_user, conversation_uid, name
    )
