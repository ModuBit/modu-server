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

from utils.config_loader import safe_load
from utils.dictionary import FrozenDictData
from .langsmith_config import langsmith_config
from .loguru_config import loguru_config
from .opentelemetry_config import ot_config, ot_instrument_loguru

app_config = FrozenDictData(safe_load('config.yml'))

# 配置日志
loguru_config(app_config.loguru)

# OT trace 配置到日志
ot_instrument_loguru()

# 配置 langsmith
langsmith_config(app_config.langsmith)

__all__ = [
    app_config,
    ot_config,
]
