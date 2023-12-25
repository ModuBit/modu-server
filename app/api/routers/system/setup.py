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
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, constr

from app_container import AppContainer
from services.system.init_service import InitService

router = APIRouter()


class InitializeCmd(BaseModel):
    # 账号名称
    name: constr(min_length=3, max_length=32, strip_whitespace=True)
    # 账号邮箱
    email: EmailStr
    # 账号密码
    password: constr(min_length=6, max_length=32, strip_whitespace=True, pattern=r'^[a-zA-Z][a-zA-Z0-9_!@#$%&*]{5,31}$')


@router.get('/setup')
@inject
def initialized_status(
        init_system: InitService = Depends(
            Provide[AppContainer.service_container.init_system]
        )
):
    """
    获取初始化信息
    :param init_system: 初始化服务
    """
    return init_system.is_initialized()


@router.post('/setup')
@inject
def initialize(
        init_data: InitializeCmd,
        init_service: InitService = Depends(
            Provide[AppContainer.service_container.init_system]
        )
):
    """
    初始化
    :param init_data: 初始化数据
    :param init_service: 初始化服务
    """
    init_service.initialize(**init_data.model_dump())
    return True
