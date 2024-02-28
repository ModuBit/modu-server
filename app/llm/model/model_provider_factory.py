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

from services.llm.models.entities.provider import Provider


class ModelProviderFactory:
    """
    LLM模型工厂
    """

    def __init__(self):
        pass

    def _get_all_providers(self) -> list[Provider]:
        """
        获取所有的Provider
        :return: Provider
        """
        pass
