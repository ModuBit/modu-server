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
from collections import OrderedDict
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Any

import yaml
from pydantic import BaseModel

from llm.model.entities.commons import I18nOption
from llm.model.entities.form import FormSchema


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

    TEXT_EMBEDDING = 'TEXT_EMBEDDING'
    """文本嵌入"""

    TEXT_TO_SPEECH = 'TEXT_TO_SPEECH'
    """文本转语音"""

    SPEECH_TO_TEXT = 'SPEECH_TO_TEXT'
    """语音转文本"""


class ModelFeature(str, enum.Enum):
    """
    模型特性
    """

    VISION = "VISION"
    """视觉识别"""


class FetchFrom(str, enum.Enum):
    """
    模型来源
    """

    PREDEFINED = "PREDEFINED"
    """系统预设"""

    CUSTOMIZABLE = "CUSTOMIZABLE"
    """用户自定义"""


class ModelSchema(BaseModel):
    """
    LLM模型
    """

    model: str
    """模型"""

    name: str
    """名称"""

    type: ModelType
    """类型"""

    fetch_from: FetchFrom = FetchFrom.PREDEFINED
    """模型来源"""

    description: I18nOption | None = None
    """描述"""

    features: list[ModelFeature] = []
    """特性"""

    properties: dict[str, Any] = []
    """属性"""

    parameters: list[FormSchema] = []
    """参数"""

    deprecated: bool = False
    """是否已过期不再可用"""


def _load_model_schemas(module_path: str) -> list[ModelSchema]:
    """
    从一个包路径中加载所有的ModelSchema
    :param module_path: 包路径
    :return: ModelSchema
    """
    return [_load_model_schema(path) for path in files(module_path).iterdir()
            if path.suffix in ['.yml', '.yaml']]


def _load_model_schema(model_schema_file: Traversable) -> ModelSchema:
    """
    从一个配置文件中加载ModelSchema
    :param model_schema_file: 配置文件
    :return: ModelSchema
    """
    schema_content = model_schema_file.read_text(encoding='utf-8')
    schema_data = yaml.safe_load(schema_content)
    return ModelSchema(**schema_data)


class LLMModel(ABC):
    """
    LLM模型
    """

    def __init__(self):
        self._model_schemas = OrderedDict()
        """该类型下模型"""

        # 加载model
        self._load_model_schemas()

    def _load_model_schemas(self):
        """
        加载该类型下所有模型
        """

        if len(self._model_schemas.items()) > 0:
            return

        module = self.__class__.__module__
        parent_module = '.'.join(module.split('.')[:-1])

        model_schemas = _load_model_schemas(parent_module)
        for model_schema in model_schemas:
            self._model_schemas[model_schema.model] = model_schema

    @property
    @abstractmethod
    def model_type(self) -> ModelType:
        """
        模型类型
        """
        raise NotImplementedError()

    @property
    def model_schemas(self) -> list[ModelSchema]:
        """获取该类型下所有的模型定义"""
        return [model_schema for (_, model_schema) in self._model_schemas.items()]

    @property
    @abstractmethod
    def description(self) -> I18nOption:
        """
        模型描述
        """
        raise NotImplementedError()
