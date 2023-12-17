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

import json
import time

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse


def register(app: FastAPI):
    @app.middleware('http')
    async def json_response(request: Request, call_next):
        """
        对于 application-json的响应进行统一响应包装
        :param request: 请求
        :param call_next: 下一个处理器
        :return: {
            success: True,
            code: 200,
            content: ''
        }
        """

        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = str(process_time)

        # 判断request accept 是否为 application/json，包装response的body内容
        if request.headers.get('accept') == 'application/json':
            # 异步读取response body
            original_body = b""
            async for chunk in response.body_iterator:
                original_body += chunk

            modified_body = {
                'success': response.status_code == 200,
                'code': response.status_code,
                'content': json.loads(original_body),
            }

            modified_headers = {name: value for name, value in response.headers.items() if
                                name.lower() != 'content-length'}

            response = JSONResponse(content=modified_body,
                                    status_code=response.status_code,
                                    headers=modified_headers)

        return response
