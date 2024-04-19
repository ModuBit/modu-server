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

from typing import TypeVar

from config import app_config
from utils.dictionary import dict_get
from utils.lifespan import register_pre_destroy_executor
from .account import AccountRepository, AccountRepositoryPostgres
from .database import Database
from .database_postgres import PostgresDatabase
from .workspace import WorkspaceRepository, WorkspaceRepositoryPostgres

RepositoryInstance = TypeVar('RepositoryInstance')

_database: Database | None = None
_database_mapping = {
    'postgres': PostgresDatabase,
}

_account_repository: AccountRepository | None = None
_account_repository_mapping = {
    'postgres': AccountRepositoryPostgres,
}

_workspace_repository: WorkspaceRepository | None = None
_workspace_repository_mapping = {
    'postgres': WorkspaceRepositoryPostgres,
}


def get_database() -> Database:
    """
    根据配置中的数据库类型创建并返回一个Database实例。

    :return: Database实例
    :raises ValueError: 如果数据库类型不受支持
    """

    global _database

    if _database:
        return _database

    database_type = app_config.repository.data.type
    if database_type not in _database_mapping:
        raise ValueError(f"Unsupported database type: {database_type}")

    config = dict_get(app_config, f"repository.data.{database_type}")
    _database = _database_mapping[database_type](**config)

    register_pre_destroy_executor(_database.close)

    return _database


def get_repository(repository_name: str) -> RepositoryInstance:
    """
    根据配置中的数据库类型创建对应的Repository实例

    :param repository_name: Repository实例名
    :raises ValueError: 如果数据库类型不受支持
    """

    global_repository_name = f"_{repository_name}_repository"
    global_repository_mapping = globals()[f"{global_repository_name}_mapping"]

    if globals()[global_repository_name]:
        return globals()[global_repository_name]

    database_type = app_config.repository.data.type
    if database_type not in global_repository_mapping:
        raise ValueError(f"Unsupported database type: {database_type}")

    repository_instance = global_repository_mapping[database_type](get_database())
    globals()[global_repository_name] = repository_instance
    return repository_instance
