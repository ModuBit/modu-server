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

import asyncio
import platform

from fastapi import FastAPI
from loguru import logger

from api.middlewares import register as middlewares_register
from api.routers import register as routers_register
from config import app_config
from config import loguru_config, ot_config, ot_instrument_loguru
from utils import lifespan
from utils.banner import banner_print


def use_uvloop_if_available():
    """
    尝试使用uvloop
    """
    if platform.system() != 'Windows':
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("[EventLoop] Using uvloop as the event loop.")
        except ImportError:
            logger.warning("[EventLoop] uvloop not installed, using default asyncio event loop.")
    else:
        logger.info("[EventLoop] Running on Windows, using default asyncio event loop.")


def create_app() -> FastAPI:
    """
    创建FastAPI实例
    :return: FastAPI实例
    """

    # 创建FastAPI实例
    fast_app = FastAPI(**(app_config.app or {}), lifespan=lifespan.lifespan)
    fast_app.config = app_config

    return fast_app


# 尝试使用uvloop
use_uvloop_if_available()

# 打印banner
banner_print('./banner.txt', app_config)

# 配置日志
loguru_config(app_config.loguru)

# OT trace 配置到日志
ot_instrument_loguru()

# 创建应用
app = create_app()

# 配置OT
ot_config(app)

# 注册路由
routers_register.register(app)

# 注册异常处理
routers_register.exception_handler(app)

# 注册中间件
middlewares_register.register(app)

if __name__ == '__main__':
    """
    本地开发使用 python main.py
    生产请使用 Gunicorn 进行部署
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
    """
    import uvicorn

    uvicorn.run(
        'main:app',
        reload=True,
        host=app_config.server.host or '0.0.0.0',
        port=app_config.server.port or 8080,
    )
