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

import repositories
import services


class AppContainer(containers.DeclarativeContainer):
    """
    应用容器
    """

    # 全局配置
    config = providers.Configuration(yaml_files=['./config.yml'])

    # 数据容器
    repository_container: repositories.RepositoryContainer = providers.Container(
        repositories.RepositoryContainer,
        config=config,
    )

    # 服务容器
    service_container: services.ServiceContainer = providers.Container(
        services.ServiceContainer,
        config=config,
        data_container=repository_container.data_container,
        oss_container=repository_container.oss_container,
        vector_container=repository_container.vector_container,
    )
