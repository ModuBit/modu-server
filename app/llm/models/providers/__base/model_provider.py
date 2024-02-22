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
from typing import Optional

import yaml

from llm.models.entities.provider import ProviderSchema


class ModelProvider(ABC):
    """
    模型提供商
    """

    _provider_schema: Optional[ProviderSchema] = None
    """供应商元数据定义"""

    def get_provider_schema(self) -> ProviderSchema:
        """
        获取供应商元数据定义
        """

        if self._provider_schema:
            return self._provider_schema

        module = self.__class__.__module__
        name = module.split('.')[-1]
        schema_data = yaml.safe_load(read_text(module, f"{name}.yml"))
        provider_schema = ProviderSchema(**schema_data)
        self._provider_schema = provider_schema

        return provider_schema
