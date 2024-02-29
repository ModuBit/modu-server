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

import uvicorn
from fastapi import FastAPI

from api.middlewares import register as middlewares_register
from api.routers import register as routers_register
from config import app_config
from config import loguru_config, ot_config, ot_instrument_loguru
from utils import lifespan
from utils.banner import banner_print


def create_app() -> FastAPI:
    """
    创建FastAPI实例
    :return: FastAPI实例
    """

    # 创建FastAPI实例
    fast_app = FastAPI(**app_config.get('app', {}), lifespan=lifespan.lifespan)
    fast_app.config = app_config

    return fast_app


# 打印banner
banner_print('./banner.txt', app_config)

# 配置日志
loguru_config(app_config.get('loguru'))

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
    """
    server_config = app_config.get('server', {})
    uvicorn.run(
        'main:app',
        reload=True,
        host=server_config.get('host', '0.0.0.0'),
        port=server_config.get('port', 8080),
    )
