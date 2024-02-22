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

from llm.models.providers.__base.model_provider import ModelProvider
from llm.models.providers.openai.openai import OpenAIProvider

from utils.reflect.module_scan import load_classes


def test_load_classes():
    model_provider_classes = load_classes('llm.models.providers', ModelProvider, True, 1)
    assert len(model_provider_classes) > 0
    assert any(model_provider_class == OpenAIProvider for model_provider_class in model_provider_classes)

    model_provider_instances = [model_provider_class() for model_provider_class in model_provider_classes]
    assert len(model_provider_instances) > 0
    assert all(
        isinstance(model_provider_instance, ModelProvider) for model_provider_instance in model_provider_instances)
    assert any(
        isinstance(model_provider_instance, OpenAIProvider) for model_provider_instance in model_provider_instances)