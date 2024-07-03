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
from datetime import datetime
from typing import AsyncIterator

from langchain_core.messages import SystemMessage, HumanMessage, BaseMessageChunk
from langchain_openai import ChatOpenAI
from starlette.responses import ContentStream

from llm.model import model_provider_factory
from services.llm import llm_provider_service


async def generate(workspace_uid: str) -> dict | ContentStream:
    provider_config = await llm_provider_service._detail(workspace_uid, "openai")
    provider_config.decrypt_credential()
    provider_credential = provider_config.provider_credential

    provider = model_provider_factory.get_provider("openai")

    model_name = "gpt-4o"
    chat_model = ChatOpenAI(model_name=model_name,
                            request_timeout=5, max_retries=0, max_tokens=512, streaming=True,
                            **provider_credential)
    aiter = chat_model.astream([
        SystemMessage(
            content="Translate the following from Chinese into English, Franch and German. Please output in both JSON format and tabular format."),
        HumanMessage(content="林中通幽境，深山藏小舍")
    ])

    async def transform_async_iterator(async_iter: AsyncIterator[BaseMessageChunk]) -> AsyncIterator[str]:
        async for message_chunk in async_iter:
            yield f'id: {datetime.now()}\nevent: message\ndata: {message_chunk.json()}\n\n'
        yield f'id: {datetime.now()}\nevent: done\n\n'

    return transform_async_iterator(aiter)
