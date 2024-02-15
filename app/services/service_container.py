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
from .system import SystemContainer


class ServiceContainer(containers.DeclarativeContainer):
    """
    服务容器
    """

    config = providers.Configuration()

    data_container: DataContainer = providers.DependenciesContainer()
    oss_container: OssContainer = providers.DependenciesContainer()
    vector_container: VectorContainer = providers.DependenciesContainer()

    # 系统容器
    system_container: SystemContainer = providers.Container(
        SystemContainer,
        config=config,
        data_container=data_container,
        oss_container=oss_container,
        vector_container=vector_container,
    )
