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
from collections.abc import Mapping

from pydantic import BaseModel

from .commons import I18nOption


class FormFieldRule(BaseModel):
    required: bool = False
    """是否必须"""

    min: int | None = None
    """最小"""

    max: int | None = None
    """最大"""

    pattern: str | None = None
    """正则规则"""

    message: I18nOption | None = None
    """规则消息"""


class FormFieldValueEnum(BaseModel):
    text: I18nOption
    """值展示文本"""

    status: str | None = None
    """状态"""

    disabled: bool = False
    """是否禁用"""


class FormSchema(BaseModel):
    """
    表单元数据
    https://pro-components.antdigital.dev/components/schema-form
    https://pro-components.antdigital.dev/components/schema
    """

    data_index: str
    """与实体映射的 key"""

    value_type: str
    """数据的渲渲染方式，字段类型"""

    value_enum: Mapping[str, FormFieldValueEnum | None] = None
    """select radio 等组件的选项"""

    field_props: Mapping[str, object | None] = None
    """对应组件 fieldProps 属性"""

    title: I18nOption | None = None
    """标题的内容，在 form 中是 label"""

    tooltip: I18nOption | None = None
    """会在 title 旁边展示一个 icon，鼠标浮动之后展示"""

    rules: FormFieldRule | None = None
    """规则"""