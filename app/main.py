"""
Copyright 2024 Maner·Fan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import uvicorn
from fastapi import FastAPI

import app_container
import routers


def create_app() -> FastAPI:
    """
    初始化Container容器
    创建FastAPI实例
    """

    # 初始化Container容器
    container = app_container.AppContainer()
    container.init_resources()

    # 创建FastAPI实例
    app = FastAPI(**container.config()["app"])
    app.container = container

    container.wire(packages=["services", "routers"])

    return app


# 创建应用
app = create_app()

# 注册路由
routers.register(app)


# 注册shutdown事件
@app.on_event("shutdown")
async def app_shutdown():
    app.container.shutdown_resources()


if __name__ == "__main__":
    """
    本地调试时使用 python main.py
    生产请使用 Gunicorn 进行部署
    """
    server_config = app.container.config()["server"]
    uvicorn.run(
        "main:app",
        reload=True,
        host=server_config["host"],
        port=server_config["port"],
    )
