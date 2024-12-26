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

import base64

from sqlalchemy import TypeDecorator, SmallInteger, String


class Bool2SmallInt(TypeDecorator):
    """
    定义 bool 与 smallint 之间的映射
    """

    impl = SmallInteger

    cache_ok = False

    def process_bind_param(self, value, dialect):
        """
        Convert Python bool to database int
        """
        return 1 if value else 0

    def process_result_value(self, value, dialect):
        """
        Convert database int to Python bool
        """
        return value != 0


class Bytes2String(TypeDecorator):
    """
    定义 bytes 与 string 之间的映射
    """

    impl = String

    def process_bind_param(self, value, dialect):
        """
        Convert Python bytes to database string
        """
        if value is not None:
            value = base64.b64encode(value).decode("utf-8")
        return value

    def process_result_value(self, value, dialect):
        """
        Convert database string to Python bytes
        """
        if value is not None:
            value = base64.b64decode(value.encode("utf-8"))
        return value
