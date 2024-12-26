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

import enum


class ErrorShowType(str, enum.Enum):
    SILENT = "SILENT"
    WARN_MESSAGE = "WARN_MESSAGE"
    ERROR_MESSAGE = "ERROR_MESSAGE"
    NOTIFICATION = "NOTIFICATION"
    REDIRECT = "REDIRECT"


class BaseServiceError(Exception):
    def __init__(
        self,
        message: str,
        show_type: ErrorShowType = ErrorShowType.ERROR_MESSAGE,
        target: str = None,
        status_code: int = 403,
    ):
        """
        :param message: 消息文案
        :param show_type: 展示类型
        :param target: 目标（如需跳转）
        :param status_code: http status code
        """
        self.show_type = show_type
        self.target = target
        self.message = message
        self.status_code = status_code


class UnauthorizedError(BaseServiceError):
    pass
