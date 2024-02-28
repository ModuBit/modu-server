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

import ast
import os
import re

import yaml

# 正则表达式用于匹配 ${variable_name[:default_value]}
_env_var_pattern = re.compile(r'\$\{([^:}]+):?([^}]*)}')


def _env_var_constructor(loader, node):
    """
    A function that accepts a Loader instance
    and a node object and produces the corresponding Python object.
    """

    value = loader.construct_scalar(node)

    def _replace_env_var(match):
        env_var, default_value = match.groups()
        # 读取环境变量，如果未设置则返回默认值
        return os.getenv(env_var, default_value)

    # 尝试转换为对应的字面量，保证数字、布尔等非字符串类型的正确
    var = _env_var_pattern.sub(_replace_env_var, value)
    if isinstance(var, str):
        try:
            return ast.literal_eval(var)
        except (ValueError, SyntaxError, TypeError):
            # 如果转换失败，返回原始字符串
            return var
    else:
        return var


# 添加构造器用于处理带有特定标签的节点
yaml.SafeLoader.add_implicit_resolver('!env_var', _env_var_pattern, None)
yaml.SafeLoader.add_constructor('!env_var', _env_var_constructor)
yaml.add_implicit_resolver('!env_var', _env_var_pattern)
yaml.add_constructor('!env_var', _env_var_constructor)


def safe_load(file_path):
    """
    支持使用 ${ENV_VAR_NAME:default}
    see yaml.safe_load
    :param file_path: 文件路径
    """
    with open(file_path, 'r') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def full_load(file_path):
    """
    支持使用 ${ENV_VAR_NAME:default}
    see yaml.load
    :param file_path: 文件路径
    """
    with open(file_path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
