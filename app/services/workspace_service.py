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

from repositories.data import workspace_repository
from repositories.data.account.account_models import Account
from repositories.data.workspace.workspace_models import Workspace, WorkspaceMemberRole
from utils.errors.account_error import UnauthorizedError
from utils.errors.space_error import SpaceExistsError


async def list_related(account: Account) -> list[Workspace]:
    """
    查询用户相关的空间
    :param account: 用户
    :return: Workspace
    """

    # 我的空间
    my_workspace = await workspace_repository.find_mine_by_creator_uid(account.uid)
    my_workspace.member_role = WorkspaceMemberRole.OWNER

    # TODO 我参与的空间

    return [my_workspace]


async def detail(current_user: Account, workspace_uid: str) -> Workspace:
    """
    查看空间详情
    :param current_user: 当前用户
    :param workspace_uid: 空间uid
    :return: Workspace
    """
    workspace = await workspace_repository.get_by_uid(workspace_uid)
    if not workspace:
        raise SpaceExistsError('该空间不存在')

    # 创建人
    if workspace.creator_uid == current_user.uid:
        workspace.member_role = WorkspaceMemberRole.OWNER
        return workspace

    # 成员
    workspace_member = await workspace_repository.get_member_by_uid(workspace_uid, current_user.uid)
    if not workspace_member:
        raise UnauthorizedError('您无该空间权限')

    workspace.member_role = workspace_member.member_role
    return workspace
