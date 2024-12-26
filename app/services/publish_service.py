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

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.data import publish_config_repository
from repositories.data.publish.publish_config import (
    PublishConfigTargetType,
    PublishConfig,
    PublishConfigStatus,
)


async def publish(
    target_type: PublishConfigTargetType,
    target_uid: str,
    config_mode: str,
    config_content: dict,
    session: AsyncSession | None = None,
) -> str:
    """
    发布
    :param target_type: 目标类型
    :param target_uid: 目标uid
    :param config_mode:  配置模式
    :param config_content: 配置内容
    :param session: Session
    :return: 配置 UID
    """
    config = PublishConfig(
        target_type=target_type,
        target_uid=target_uid,
        config_mode=config_mode,
        config_content=config_content,
        publish_status=PublishConfigStatus.PUBLISHED,
    )

    await publish_config_repository.save_or_update(
        config, PublishConfigStatus.PUBLISHED, session
    )
    return config.uid


async def save(
    target_type: PublishConfigTargetType,
    target_uid: str,
    config_mode: str,
    config_content: dict,
) -> str:
    """
    保存
    :param target_type: 目标类型
    :param target_uid: 目标uid
    :param config_mode:  配置模式
    :param config_content: 配置内容
    :return: 配置 UID
    """
    config = PublishConfig(
        target_type=target_type,
        target_uid=target_uid,
        config_mode=config_mode,
        config_content=config_content,
        publish_status=PublishConfigStatus.PUBLISHED,
    )

    await publish_config_repository.save_or_update(config, PublishConfigStatus.DRAFT)
    return config.uid
