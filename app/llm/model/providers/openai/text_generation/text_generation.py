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

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from loguru import logger

from llm.model.entities.models import TextGenerationModel
from utils.errors.llm_error import LLMValidateError


class OpenAITextGenerationModel(TextGenerationModel):
    async def validate_credentials(self, credentials: dict, model: str | None = None) -> None:
        try:
            chat_model = ChatOpenAI(model_name=model or "gpt-4o",
                                    request_timeout=5, max_retries=0, max_tokens=512,
                                    **credentials)
            chat_result = await chat_model.ainvoke([
                SystemMessage(content="Translate the following from Chinese into English"),
                HumanMessage(content="林中通幽境，深山藏小舍")
            ])
            logger.info("OpenAI Credential Validate Success, using model {}, chat result {}",
                        model or "gpt-4o", chat_result)
        except Exception as e:
            raise LLMValidateError(f"认证异常: {e}")
