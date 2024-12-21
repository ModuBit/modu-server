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

from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils.dictionary import dict_merge


class CamelCaseJSONResponse(JSONResponse):
    """
    将基于 pydantic BaseModel 的对象属性，从下划线风格转为驼峰风格
    """

    def render(self, content: Any) -> bytes:
        content = CamelCaseJSONResponse._convert_to_dict(content)
        return super().render(content)

    @staticmethod
    def _convert_to_dict(obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            # 前提：需要实现 alias_generator
            return obj.model_dump(by_alias=False)
        elif isinstance(obj, dict):
            return {key: CamelCaseJSONResponse._convert_to_dict(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [CamelCaseJSONResponse._convert_to_dict(item) for item in obj]
        else:
            return obj


def default_model_config(extra_model_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    默认的 pydantic model_config
    :param extra_model_config: 额外的 model_config
    :return: model_config
    """
    default_config = {
        # 别名生成（下划线转驼峰）
        # "alias_generator": _to_camel_case,
        # 允许在反序列化时也使用别名
        "populate_by_name": True
    }
    return dict_merge(default_config, extra_model_config, True)


def _to_camel_case(string: str) -> str:
    """
    将下划线命名转为驼峰命名
    to_camel_case          →    toCamelCase
    _to_camel_case_        →    _toCamelCase_
    __to_camel_case__      →    __toCamelCase__
    __to__camel__case__    →    __toCamelCase__
    """

    # 保留首尾的下划线
    leading_underscores = len(string) - len(string.lstrip('_'))
    trailing_underscores = len(string) - len(string.rstrip('_'))

    parts = string.strip('_').split('_')
    # 过滤掉空字符串部分，以防止在处理连续下划线时出现问题
    filtered_parts = [part for part in parts if part]
    if not filtered_parts:
        # 如果过滤后没有剩余的部分，返回带有原始首尾下划线的原始字符串
        return "_" * leading_underscores + "_" * trailing_underscores

    # 非首尾下划线转驼峰
    camel_case = filtered_parts[0] + ''.join(word.capitalize() for word in filtered_parts[1:])
    return "_" * leading_underscores + camel_case + "_" * trailing_underscores
