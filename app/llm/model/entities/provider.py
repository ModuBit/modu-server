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

from abc import ABC
from collections import OrderedDict
from importlib.resources import files

import yaml
from pydantic import BaseModel

from utils.reflect.module_scan import load_classes
from .commons import I18nOption, IconOption, HelpOption
from .form import FormSchema
from .model import LLMModel, ModelType


class ProviderSchema(BaseModel):
    """
    LLM提供商
    """

    provider: str
    """标识"""

    name: str
    """名称"""

    description: I18nOption | None = None
    """描述"""

    icon: IconOption | None = None
    """图标"""

    help: HelpOption | None = None
    """帮助"""

    credential_schemas: list[FormSchema] = []
    """凭证"""

    supported_model_types: list[ModelType] = []
    """支持的模型类型"""


class LLMProvider(ABC):
    """
    模型提供商
    """

    def __init__(self):
        self._provider_schema = None
        """提供商元数据定义"""

        self._models = OrderedDict()
        """提供商模型"""

        # 加载model
        self._load_models()

    def _load_models(self):
        """
        加载所有的模型
        """

        # 加载model
        module = self.__class__.__module__
        parent_module = '.'.join(module.split('.')[:-1])
        model_classes = load_classes(parent_module, LLMModel, True, 1)
        models = [provider_cls() for provider_cls in model_classes]

        # 对model进行去重处理
        model_groups = {}
        for model in models:
            model_groups[model.model_type] = model

        # 对model进行排序
        ordinal_list = [name for name, _ in ModelType.__members__.items()]
        ordering = {key: index for index, key in enumerate(ordinal_list)}
        ordering_default = float('inf')
        sorted_groups = sorted(model_groups.items(), key=lambda item: ordering.get(item[0], ordering_default))

        for model_type, model in sorted_groups:
            self._models[model_type] = model

    @property
    def models(self) -> list[LLMModel]:
        """
        获取该Provider下所有的模型
        """
        return [model for (_, model) in self._models.items()]

    @property
    def provider_schema(self) -> ProviderSchema:
        """
        获取提供商元数据定义
        """

        if self._provider_schema:
            return self._provider_schema

        module = self.__class__.__module__
        parent_module = '.'.join(module.split('.')[:-1])
        name = parent_module.split('.')[-1]

        schema_content = files(parent_module).joinpath(f"{name}.yml").read_text(encoding='utf-8')
        schema_data = yaml.safe_load(schema_content)
        provider_schema = ProviderSchema(**schema_data, supported_model_types=self._models.keys())
        self._provider_schema = provider_schema

        return provider_schema
