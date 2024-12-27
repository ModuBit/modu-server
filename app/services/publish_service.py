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


async def get_draft(
    target_type: PublishConfigTargetType,
    target_uid: str,
) -> PublishConfig:
    """
    获取草稿
    :param target_type: 目标类型
    :param target_uid: 目标uid
    :return: PublishConfig
    """
    return await publish_config_repository.get_draft(target_type, target_uid)


async def get_version(
    target_type: PublishConfigTargetType,
    target_uid: str,
    version_uid: str | None = None,
) -> PublishConfig:
    """
    获取特定版本
    :param target_type: 目标类型
    :param target_uid: 目标uid
    :param version_uid: 版本uid 缺省获取草稿
    :return: PublishConfig
    """
    if version_uid:
        return await publish_config_repository.get_version(
            target_type, target_uid, version_uid
        )
    else:
        return await publish_config_repository.get_draft(target_type, target_uid)


async def list_versions(
    target_type: PublishConfigTargetType,
    target_uid: str,
    top: int = 20,
) -> list[PublishConfig]:
    """
    获取版本列表
    :param target_type: 目标类型
    :param target_uid: 目标uid
    :param top: 数量 缺省 20
    :return: list[PublishConfig]
    """
    return await publish_config_repository.list_versions(target_type, target_uid, top)


async def publish(
    target_type: PublishConfigTargetType,
    target_uid: str,
    config: dict,
    creator_uid: str,
    session: AsyncSession | None = None,
) -> str:
    """
    发布
    :param target_type: 目标类型
    :param target_uid: 目标uid
    :param config: 配置
    :param creator_uid: 创建者UID
    :param session: Session
    :return: 配置 UID
    """
    config = PublishConfig(
        target_type=target_type,
        target_uid=target_uid,
        config=config,
        creator_uid=creator_uid,
        publish_status=PublishConfigStatus.PUBLISHED,
    )

    await publish_config_repository.save_or_update(
        config, PublishConfigStatus.PUBLISHED, session
    )
    return config.uid


async def save(
    target_type: PublishConfigTargetType,
    target_uid: str,
    config: dict,
    creator_uid: str,
) -> str:
    """
    保存
    :param target_type: 目标类型
    :param target_uid: 目标uid
    :param config: 配置
    :param creator_uid: 创建者UID
    :return: 配置 UID
    """
    config = PublishConfig(
        target_type=target_type,
        target_uid=target_uid,
        config=config,
        creator_uid=creator_uid,
        publish_status=PublishConfigStatus.PUBLISHED,
    )

    await publish_config_repository.save_or_update(config, PublishConfigStatus.DRAFT)
    return config.uid
