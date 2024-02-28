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
import re

from loguru import logger

from utils.dictionary import dict_get

# 正则表达式用于匹配 ${variable_name[:default_value]}
_env_var_pattern = re.compile(r'\$\{([^:}]+):?([^}]*)}')


def _replace_env_var(match, config: dict):
    variable, default_value = match.groups()
    # 读取顺序 config -> env -> default
    return dict_get(config, variable, os.getenv(variable, default_value))


def banner_print(banner_file: str, config: dict):
    """
    打印banner信息
    :param banner_file: banner文件
    :param config: 配置
    """
    with open(banner_file, "r") as banner_file:
        banner = banner_file.read()
        display_banner = _env_var_pattern.sub(lambda match: _replace_env_var(match, config), banner)
        logger.info(display_banner)
