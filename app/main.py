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

import logging.config
from contextlib import asynccontextmanager

import uvicorn
import yaml
from fastapi import FastAPI

import app_container
from api.routers import register

# 日志配置
with open('logging.yml', 'r') as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """
    FastAPI生命周期
    :param fast_app: FastAPI
    """

    # start
    # 应用启动之后

    yield

    # shutdown
    # 应用关闭之前
    fast_app.container.shutdown_resources()


def create_app() -> FastAPI:
    """
    初始化Container容器
    创建FastAPI实例
    :return: FastAPI实例
    """

    # 初始化Container容器
    container = app_container.AppContainer()
    container.init_resources()

    # 创建FastAPI实例
    fast_app = FastAPI(**container.config()['app'], lifespan=lifespan)
    fast_app.container = container

    # 注入依赖
    container.wire(packages=['api', 'services', 'repositories'])

    return fast_app


# 创建应用
app = create_app()

# 注册路由
register.register(app)

# 注册异常处理
register.exception_handler(app)

if __name__ == '__main__':
    """
    本地开发使用 python main.py
    生产请使用 Gunicorn 进行部署
    """
    server_config = app.container.config()['server']
    uvicorn.run(
        'main:app',
        reload=True,
        host=server_config['host'],
        port=server_config['port'],
    )
