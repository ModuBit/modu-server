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
from importlib.resources import read_text

import yaml
from pydantic import BaseModel

from .commons import I18nOption, IconOption, HelpOption
from .form import FormSchema


class ProviderSchema(BaseModel):
    """
    LLM供应商
    """

    key: str
    """标识"""

    name: I18nOption
    """名称"""

    description: I18nOption | None = None
    """描述"""

    icon: IconOption | None = None
    """图标"""

    help: HelpOption | None = None
    """帮助"""

    credential_schemas: list[FormSchema] | None = None
    """凭证"""


class ModelProvider(ABC):
    """
    模型提供商
    """

    _provider_schema: ProviderSchema | None = None
    """供应商元数据定义"""

    def get_provider_schema(self) -> ProviderSchema:
        """
        获取供应商元数据定义
        """

        if self._provider_schema:
            return self._provider_schema

        module = self.__class__.__module__
        parent_module = '.'.join(module.split('.')[:-1])
        name = parent_module.split('.')[-1]
        schema_data = yaml.safe_load(read_text(parent_module, f"{name}.yml"))
        provider_schema = ProviderSchema(**schema_data)
        self._provider_schema = provider_schema

        return provider_schema
