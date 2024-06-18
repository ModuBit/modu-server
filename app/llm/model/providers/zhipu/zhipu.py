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

from llm.model.entities.model import ModelType
from llm.model.entities.provider import LLMProvider

ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"


class ZhiPuProvider(LLMProvider):
    """
    智普清言
    """

    async def validate_credentials(self, credentials: dict) -> None:
        text_generation_model = self.get_model(ModelType.TEXT_GENERATION)
        await text_generation_model.validate_credentials(credentials)
