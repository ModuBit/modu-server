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

import uuid
from datetime import datetime

from ulid import ULID

from repositories.data.workspace.WorkspaceRepositoryPostgres import WorkspacePO
from repositories.data.workspace.workspace_models import WorkspaceType, Workspace
from utils import json


def test_json_1():
    workspace_model = WorkspacePO(
        id=uuid.uuid1(),
        uid=str(ULID()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_deleted=False,
        creator_uid=str(ULID()),
        name='workspace name',
        description='workspace description',
        type=WorkspaceType.PRIVATE
    )
    workspace = Workspace(**workspace_model.as_dict())

    print(workspace)

    workspace_json_str = json.dumps(workspace.model_dump())
    print(workspace_json_str)

    workspace_loads = json.loads(workspace_json_str)
    print(workspace_loads)

def test_json_2():
    workspace_model = WorkspacePO(
        id=uuid.uuid1(),
        uid=str(ULID()),
        updated_at=datetime.now(),
        is_deleted=False,
        creator_uid=str(ULID()),
        name='workspace name',
        description='workspace description',
        type=WorkspaceType.PRIVATE
    )
    workspace = Workspace(**workspace_model.as_dict())

    print(workspace)

    workspace_json_str = json.dumps(workspace.model_dump())
    print(workspace_json_str)

    workspace_loads = json.loads(workspace_json_str)
    print(workspace_loads)


