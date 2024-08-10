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

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel

from llm.model.entities.commons import I18nOption
from llm.model.entities.model import LLMModel, ModelType


class TextGenerationModel(LLMModel, ABC):
    """
    文本生成 模型
    """

    @property
    def model_type(self) -> ModelType:
        return ModelType.TEXT_GENERATION

    @property
    def description(self) -> I18nOption:
        return I18nOption(default='文本生成', en_us='Text Generation')

    @abstractmethod
    def chat_model(self,
                   provider_credential: dict, model_parameters: dict, model_name: str,
                   streaming: bool = True, request_timeout: int = 10, max_retries: int = 0) -> BaseChatModel:
        """
        构造BaseChatModel
        :param provider_credential: Provider凭证
        :param model_parameters: Model参数
        :param model_name: 模型名称
        :param streaming: 是否流式输出
        :param request_timeout: 请求超时时间
        :param max_retries: 最大重试次数
        :return: BaseChatModel
        """
        raise NotImplementedError()
