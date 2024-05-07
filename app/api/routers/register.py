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

from fastapi import FastAPI, Depends
from fastapi.exceptions import ValidationException
from loguru import logger
from sqlalchemy.exc import DBAPIError
from starlette.responses import JSONResponse

from utils.errors.base_error import BaseServiceError
from .auth import login, users
from .llm import llm_schema
from .system import setup, system
from .workspace import workspace
from ..dependencies.principal import token_verify


def register(app: FastAPI):
    """
    注册路由
    :param app:  FastAPI
    """

    app.include_router(setup.router, prefix='/api/system',
                       tags=['init | 初始化'])

    app.include_router(system.router, prefix='/api/system',
                       tags=['system | 系统信息'])
    app.include_router(llm_schema.router, prefix='/api/system/llm',
                       tags=['system | 系统信息'])

    app.include_router(login.router, prefix='/api',
                       tags=['auth | 认证'])

    app.include_router(users.router, prefix='/api/user',
                       dependencies=[Depends(token_verify)],
                       tags=['user | 用户'])

    app.include_router(workspace.router, prefix='/api/workspace',
                       dependencies=[Depends(token_verify)],
                       tags=['workspace | 空间'])


def exception_handler(app: FastAPI):
    """
    定义全局异常处理
    :param app:  FastAPI
    """

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request, exc: ValidationException):
        """
        参数验证异常
        """
        logger.warning('RequestValidationError {}, {}', exc.__class__, str(exc))
        return JSONResponse(exc.errors(), status_code=422)

    @app.exception_handler(BaseServiceError)
    async def service_exception_handler(request, exc: BaseServiceError):
        """
        业务异常
        """
        logger.warning('ServiceError {}, {}', exc.__class__, exc.message)
        return JSONResponse({'message': exc.message, 'show_type': exc.show_type, 'target': exc.target},
                            status_code=exc.status_code)

    @app.exception_handler(DBAPIError)
    async def sql_exception_handler(request, exc: DBAPIError):
        """
        SQL数据库异常
        """
        logger.exception('SQLError 服务异常 {}', str(exc))
        return JSONResponse({'message': '服务异常，请稍候重试'}, status_code=500)

    @app.exception_handler(Exception)
    async def common_exception_handler(request, exc: Exception):
        """
        其他系统异常
        """
        logger.exception('ExceptionError 服务异常 {}', str(exc))
        return JSONResponse({'message': '服务异常，请稍候重试'}, status_code=500)
