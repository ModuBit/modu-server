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

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.responses import StreamingResponse
from loguru import logger
from starlette.responses import ContentStream

from api.dependencies.principal import current_account
from repositories.data.account.account_models import Account
from repositories.data.message.message_models import Message
from services import llm_generate_service, workspace_service
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
            "Content-Encoding": "identity"
        })


@logger.catch()
@router.post(path='/chat')
async def chat(workspace_uid: str | None, chat_generate_cmd: GenerateCmd,
               current_user: Account = Depends(current_account)):
    if not workspace_uid:
        mine_workspace = await workspace_service.mine(current_user)
        if not mine_workspace:
            raise UnauthorizedError('找不到您的个人空间，请联系管理员')
        workspace_uid = mine_workspace.uid
    else:
        member_role = await workspace_service.member_role(current_user, workspace_uid)
        if member_role is None:
            raise UnauthorizedError('您无该使用该空间')

    generator = await llm_generate_service.generate(current_user, workspace_uid, chat_generate_cmd)
    response = compact_async_generate_response(generator)
    return response


@logger.catch()
@router.post(path='/chat/{conversation_uid}/message/clear')
async def clear_memory(conversation_uid: str, current_user: Account = Depends(current_account)) -> list[Message]:
    """
    清除会话记忆
    """
    return await llm_generate_service.clear_memory(current_user, conversation_uid)
