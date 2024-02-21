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

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel, EmailStr, constr

from services import init_service

router = APIRouter()


class InitializeCmd(BaseModel):
    # 账号名称
    name: constr(min_length=3, max_length=32, strip_whitespace=True)
    # 账号邮箱
    email: EmailStr
    # 账号密码
    password: constr(min_length=6, max_length=32, strip_whitespace=True, pattern=r'^[a-zA-Z][a-zA-Z0-9_!@#$%&*]{5,31}$')


@logger.catch()
@router.get('/setup')
def initialized_status():
    """
    获取初始化信息
    """
    return init_service.is_initialized()


@logger.catch()
@router.post('/setup')
def initialize(init_data: InitializeCmd):
    """
    初始化
    :param init_data: 初始化数据
    """
    init_service.initialize(**init_data.model_dump())
    return True
