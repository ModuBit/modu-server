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

import sys

from loguru import logger


def loguru_config(config: dict):
    """
    日志配置
    """
    # 先移除自动生成的配置
    logger.remove()
    # 再添加新配置
    logger.add(**config)
    logger.add(sys.stdout, format=config['format'])