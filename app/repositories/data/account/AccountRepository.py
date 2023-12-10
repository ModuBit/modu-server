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

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from .account_models import Account


class AccountRepository(ABC):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self._session_factory = session_factory

    @abstractmethod
    def find_one_by_email(self, email: str) -> Account:
        """
        通过email查找账号
        :param email: 邮箱
        :return: 账号
        """
        pass
