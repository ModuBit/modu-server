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

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from utils.errors.base_error import BaseServiceError
from . import auth

log = logging.getLogger()


def register(app: FastAPI):
    """
    注册路由
    :param app:  FastAPI
    """

    exception_handler(app)

    app.include_router(auth.login.router, prefix='/api', tags=['auth | 认证'])
    app.include_router(auth.users.router, prefix='/api/user', tags=['user | 用户'])


def exception_handler(app: FastAPI):
    """
    定义全局异常处理
    :param app:  FastAPI
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        log.warning('RequestValidationError %s, %s', exc.__class__, str(exc))
        return JSONResponse(str(exc), status_code=400)

    @app.exception_handler(BaseServiceError)
    async def service_exception_handler(request, exc: BaseServiceError):
        log.warning('ServiceError %s, %s', exc.__class__, exc.message)
        return JSONResponse({'message': exc.message}, status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def common_exception_handler(request, exc: Exception):
        log.exception('ExceptionError %s', str(exc))
        return JSONResponse({'message': str(exc)}, status_code=500)
