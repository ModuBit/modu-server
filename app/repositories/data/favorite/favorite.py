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

from datetime import datetime
import enum
from pydantic import BaseModel

from utils.pydantic import default_model_config

class FavoriteTargetType(str, enum.Enum):
    """
    收藏目标类型
    """

    BOT = "BOT"


class Favorite(BaseModel):
    """
    收藏
    """

    uid: str | None = None
    """UID"""
    created_at: datetime | None = None
    """创建时间"""
    target_type: FavoriteTargetType
    """目标类型"""
    target_uid: str
    """目标uid"""

    # 定义配置
    model_config = default_model_config()
