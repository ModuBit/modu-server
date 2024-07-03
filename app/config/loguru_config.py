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

import os
import sys

from loguru import logger

from utils.dictionary import dict_get


def loguru_config(config: dict):
    """
    日志配置
    """

    # 按进程号存储，避免使用 gunicorn 时多个进程输出到同一个文件
    base, ext = os.path.splitext(dict_get(config, 'sink', 'logs/app.log'))
    sink = f"{base}.{os.getpid()}{ext}"

    # 先移除自动生成的配置
    logger.remove()
    # 再添加新配置
    logger.add(**{**config, "sink": sink})
    logger.add(sys.stdout, format=config['format'])
