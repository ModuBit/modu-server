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

from pydantic import BaseModel

from utils.pydantic import default_model_config


class I18nOption(BaseModel):
    """
    国际化
    """
    default: str
    en_us: str | None = None
    zh_cn: str | None = None

    # 定义配置
    model_config = default_model_config()


class IconOption(BaseModel):
    """
    图标
    """
    icon: str | None = None
    avatar: str | None = None
    combine: str | None = None
    color: str | None = None

    # 定义配置
    model_config = default_model_config()


class HelpOption(BaseModel):
    """
    帮助
    """
    title: I18nOption
    """标题"""
    url: str
    """链接"""

    # 定义配置
    model_config = default_model_config()
