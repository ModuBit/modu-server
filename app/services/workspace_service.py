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

from repositories.cache import cache_decorator_builder
from repositories.cache.cache import CacheDecorator
from repositories.data import workspace_repository
from repositories.data.account.account_models import Account
from repositories.data.workspace.workspace_models import Workspace, WorkspaceMemberRole
from utils import json
from utils.errors.base_error import UnauthorizedError
from utils.errors.space_error import SpaceExistsError
from utils.json import default_excluded_fields

workspace_detail_cache: CacheDecorator[Workspace] = cache_decorator_builder.build(
    serialize=lambda workspace: workspace.model_dump_json(
        exclude=default_excluded_fields
    ),
    deserialize=lambda json_content: Workspace.model_validate_json(json_content),
    default_expire_seconds=24 * 3600,
    allow_none_values=True,
)

workspace_related_cache: CacheDecorator[list[Workspace]] = (
    cache_decorator_builder.build(
        serialize=lambda workspaces: json.dumps(
            [
                workspace.model_dump(exclude=default_excluded_fields)
                for workspace in workspaces
            ]
        ),
        deserialize=lambda json_contents: [
            Workspace.model_validate(json_obj) for json_obj in json.loads(json_contents)
        ],
        default_expire_seconds=24 * 3600,
        allow_none_values=True,
    )
)


# FIXME 关联的空间可能很多，终有一天需要分页的时候需要重新考虑缓存设计
@workspace_related_cache.async_cacheable(
    key_generator=lambda current_user, **kwargs: f"workspace:account:{current_user.uid}:workspace_related"
)
async def list_related(current_user: Account) -> list[Workspace]:
    """
    查询用户相关的空间
    :param current_user: 用户
    :return: Workspace
    """

    # 我的空间
    my_workspace = await mine(current_user)

    # TODO 我参与的空间

    return [my_workspace]


@workspace_detail_cache.async_cacheable(
    key_generator=lambda current_user, **kwargs: f"workspace:own:account:{current_user.uid}:workspace_detail"
)
async def mine(current_user: Account) -> Workspace:
    """
    查询用户创建的空间
    :param current_user: 用户
    :return: Workspace
    """

    my_workspace = await workspace_repository.find_mine_by_creator_uid(current_user.uid)
    my_workspace.member_role = WorkspaceMemberRole.OWNER

    return my_workspace


@workspace_detail_cache.async_cacheable(
    key_generator=lambda current_user, workspace_uid, **kwargs: f"workspace:{workspace_uid}:account:{current_user.uid}:workspace_detail"
)
async def detail(current_user: Account, workspace_uid: str) -> Workspace:
    """
    查看空间详情
    :param current_user: 当前用户
    :param workspace_uid: 空间uid
    :return: Workspace
    """
    workspace = await workspace_repository.get_by_uid(workspace_uid)
    if not workspace:
        raise SpaceExistsError("该空间不存在")

    # 创建人
    if workspace.creator_uid == current_user.uid:
        workspace.member_role = WorkspaceMemberRole.OWNER
        return workspace

    # 成员
    workspace_member = await workspace_repository.get_member_by_uid(
        workspace_uid, current_user.uid
    )
    if not workspace_member:
        raise UnauthorizedError("您无该空间权限")

    workspace.member_role = workspace_member.member_role
    return workspace


async def member_role(
    current_user: Account, workspace_uid: str
) -> WorkspaceMemberRole | None:
    """
    获取空间成员角色
    :param current_user: 当前用户
    :param workspace_uid: 空间uid
    :return: WorkspaceMemberRole
    """
    workspace = await detail(current_user, workspace_uid)
    return workspace.member_role if workspace else None
