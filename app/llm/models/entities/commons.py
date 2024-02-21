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


class I18nOption(BaseModel):
    """
    国际化
    """
    default: str
    en_us: Optional[str] = None
    zh_cn: Optional[str] = None


class IconOption(BaseModel):
    """
    图标
    """

    class Icon(BaseModel):
        """
        图标
        """
        default: str
        en_us: Optional[str] = None
        zh_cn: Optional[str] = None

    small: Icon
    large: Icon


class HelpOption(BaseModel):
    """
    帮助
    """
    title: I18nOption
    """标题"""
    url: str
    """链接"""
