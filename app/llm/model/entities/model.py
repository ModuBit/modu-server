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

import enum
from abc import ABC, abstractmethod

from pydantic import BaseModel


class ModelType(str, enum.Enum):
    """
    模型类型
    """

    TEXT_GENERATION = 'TEXT_GENERATION'
    """文本生成"""

    IMAGE_GENERATION = 'IMAGE_GENERATION'
    """图像生成"""

    VISION = 'VISION'
    """视觉识别"""

    EMBEDDING = 'EMBEDDING'
    """嵌入"""

    TEXT_TO_SPEECH = 'TEXT_TO_SPEECH'
    """文本转语音"""

    SPEECH_TO_TEXT = 'SPEECH_TO_TEXT'
    """语音转文本"""


class ModelSchema(BaseModel):
    pass


class LLMModel(ABC):
    @property
    @abstractmethod
    def model_type(self) -> ModelType:
        """
        模型类型
        """
        raise NotImplementedError()
