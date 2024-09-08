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
from typing import Any, TypeVar, Callable

import yaml
from pydantic import BaseModel

from llm.model.entities.commons import I18nOption, HelpOption
from llm.model.entities.form import FormSchema
from utils.dictionary import dict_get, dict_merge


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

    help: HelpOption | None = None
    """帮助"""

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


T = TypeVar('T')


def _load_module_configs(module_path: str, load: Callable[[Traversable], T]) -> list[ModelSchema]:
    """
    从一个包路径中加载所有的ModelSchema
    :param module_path: 包路径
    :return: ModelSchema
    """
    return [load(path) for path in files(module_path).iterdir()
            if path.suffix in ['.yml', '.yaml']]


def _load_model_schema(model_schema_file: Traversable) -> ModelSchema:
    """
    从一个配置文件中加载ModelSchema
    :param model_schema_file: 配置文件
    :return: ModelSchema
    """
    schema_content = model_schema_file.read_text(encoding='utf-8')
    schema_data = yaml.safe_load(schema_content)
    model_schema = ModelSchema(**schema_data)

    # 模板
    model_templates = LLMModel._model_templates[model_schema.type] \
        if model_schema.type in LLMModel._model_templates else {}

    # 处理parameters，与模板整合
    merged_parameters = [FormSchema(**dict_merge(
        dict_get(model_templates, parameter.template, FormSchema(name=parameter.name)).model_dump(),
        parameter.model_dump(),
        True
    )) if parameter.template else parameter for parameter in model_schema.parameters]
    model_schema.parameters = merged_parameters

    return model_schema


def _load_model_template(model_template_file: Traversable):
    """
    从一个配置文件中加载ModelSchema模板
    :param model_template_file: 配置模板
    :return: ModelSchema
    """
    template_content = model_template_file.read_text(encoding='utf-8')
    template_data = yaml.safe_load(template_content)
    return {
        "type": ModelType(dict_get(template_data, 'type', ).upper()),
        "parameters": {dict_get(parameter, 'name', ): FormSchema(**parameter) for parameter in
                       dict_get(template_data, 'parameters', [])}
    }


def _load_model_templates():
    """
    加载模型模板
    """

    parent_module = __package__

    model_templates = _load_module_configs(parent_module + '.templates', _load_model_template)
    return {model_template['type']: model_template['parameters'] for model_template in model_templates}


class LLMModel(ABC):
    """
    LLM模型
    """

    _model_templates: dict[ModelType, dict[str, list[FormSchema]]] = _load_model_templates()

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

        model_schemas = _load_module_configs(parent_module, _load_model_schema)
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

    @abstractmethod
    async def validate_credentials(self, credentials: dict, model: str | None = None) -> None:
        """
        验证凭证
        :param model: 模型
        :param credentials: 凭证
        """
        raise NotImplementedError()
