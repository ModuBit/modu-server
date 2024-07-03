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

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.responses import StreamingResponse
from loguru import logger
from starlette.responses import ContentStream

from api.dependencies.principal import current_account
from repositories.data.account.account_models import Account
from services.llm import llm_generate_service

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
async def chat(workspace_uid: str):
    generator = await llm_generate_service.generate(workspace_uid)
    response = compact_async_generate_response(generator)
    return response
