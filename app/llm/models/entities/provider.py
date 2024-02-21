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

from typing import Optional

from pydantic import BaseModel

from .commons import I18nOption, IconOption, HelpOption
from .form import FormSchema


class Provider(BaseModel):
    """
    LLM供应商
    """

    key: str
    """标识"""

    name: I18nOption
    """名称"""

    description: Optional[I18nOption] = None
    """描述"""

    icon: Optional[IconOption] = None
    """图标"""

    help: Optional[HelpOption] = None
    """帮助"""

    credential_schemas: Optional[list[FormSchema]] = None
    """凭证"""
