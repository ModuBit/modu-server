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

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel

from api.dependencies.principal import current_account
from repositories.data.account.account_models import Account
from repositories.data.workspace.workspace_models import Workspace, WorkspaceType, WorkspaceMemberRole
from services import workspace_service

router = APIRouter()


class WorkspaceDTO(BaseModel):
    uid: str
    """空间ID"""
    creator_uid: str
    """创建人"""
    name: str
    """空间名称"""
    description: str | None = None
    """空间简介"""
    type: WorkspaceType
    """空间类型"""
    member_role: WorkspaceMemberRole
    """空间角色"""


@logger.catch()
@router.get(path='', response_model=list[WorkspaceDTO])
async def list_related(current_user: Account = Depends(current_account)) -> list[Workspace]:
    """
    当前登录人相关的空间列表
    :param current_user: 当前用户
    :return: Workspace
    """
    return await workspace_service.list_related(current_user)


@logger.catch()
@router.get(path='/{workspace_uid}', response_model=WorkspaceDTO)
async def detail(workspace_uid: str, current_user: Account = Depends(current_account)) -> Workspace:
    """
    获取空间详情
    :param workspace_uid: 空间uid
    :param current_user: 当前用户
    :return: Workspace
    """
    return await workspace_service.detail(current_user, workspace_uid)
