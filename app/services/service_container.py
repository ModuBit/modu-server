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

from repositories import DataContainer, OssContainer, VectorContainer
from .account.account_service import AccountService
from .system.init_service import InitService
from .team.team_service import TeamService


class ServiceContainer(containers.DeclarativeContainer):
    """
    服务容器
    """

    config = providers.Configuration()

    data_container: DataContainer = providers.DependenciesContainer()
    oss_container: OssContainer = providers.DependenciesContainer()
    vector_container: VectorContainer = providers.DependenciesContainer()

    # 初始化服务
    init_system: InitService = providers.Singleton(
        InitService,
        account_repository=data_container.account_repository,
        team_repository=data_container.team_repository
    )

    # 账号服务
    account_service: AccountService = providers.Singleton(
        AccountService,
        account_repository=data_container.account_repository,
        jwt_config=config.security.jwt,
    )

    # 团队服务
    team_service: TeamService = providers.Singleton(
        TeamService,
        team_repository=data_container.team_repository
    )
