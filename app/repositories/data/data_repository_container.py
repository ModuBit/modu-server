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

from dependency_injector import containers, providers

from .account.AccountRepository import AccountRepository
from .account.AccountRepositoryPostgres import AccountRepositoryPostgres
from .data_base_pg import PgDatabase


class DataContainer(containers.DeclarativeContainer):
    """
    数据容器
    """

    config = providers.Configuration()

    db_pg = providers.Singleton(
        PgDatabase,
        host=config.repository.data.postgres.host,
        port=config.repository.data.postgres.port,
        database=config.repository.data.postgres.database,
        username=config.repository.data.postgres.username,
        password=config.repository.data.postgres.password,
    )

    # 账号
    account_repository: AccountRepository = providers.Selector(
        config.repository.data.type,
        postgres=providers.Singleton(AccountRepositoryPostgres, session_factory=db_pg.provided.session)
    )
