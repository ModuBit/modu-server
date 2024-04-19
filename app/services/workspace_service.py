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
from repositories.data.workspace.workspace_models import Workspace, WorkspaceMemberRole


def create(workspace: Workspace):
    workspace_repository.create(workspace)


def add_space_membership(workspace_uid: str, member_uid: str, role: WorkspaceMemberRole):
    workspace_repository.add_workspace_membership(
        workspace_uid, member_uid,
        WorkspaceMemberRole.MEMBER if role == WorkspaceMemberRole.OWNER else role)
