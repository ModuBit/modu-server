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
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from functools import wraps
from typing import Callable, TypeVar, Awaitable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, DeclarativeBase
from ulid import ULID

T = TypeVar('T')


class Database(ABC):
    """
    数据库基类
    """

    @abstractmethod
    def get_async_session(self) -> AsyncSession:
        """
        获取Session
        :return: Session
        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """
        关闭数据库
        """
        raise NotImplementedError

    @asynccontextmanager
    async def async_session(self) -> Callable[..., AbstractAsyncContextManager[Session]]:
        """
        构建Session上下文
        """
        _session: AsyncSession = self.get_async_session()
        try:
            yield _session
            await _session.commit()
        except Exception:
            logger.exception("Session rollback because of exception")
            await _session.rollback()
            raise
        finally:
            await _session.close()


class Repository(ABC):
    """
    数据库存储基类
    """

    def __init__(self, database: Database):
        self._database = database


def with_async_session(func: Callable[..., Awaitable],):
    """
    Session装饰器
    只能用在Repository类方法中
    :param func: async func(self, session, ...)
    """

    @wraps(func)
    async def wrapper(self: Repository, *args, **kwargs):
        # 检查位置参数中是否存在Session对象
        if any(isinstance(arg, AsyncSession) for arg in args):
            return await func(self, *args, **kwargs)

        # 检查关键字参数中是否存在名为session的对象
        if 'session' in kwargs and isinstance(kwargs['session'], AsyncSession):
            return await func(self, *args, **kwargs)

        # 如果没有找到Session对象，则创建一个新的Session对象
        async with self._database.async_session() as session:
            kwargs['session'] = session
            return await func(self, *args, **kwargs)

    return wrapper


class BasePO(DeclarativeBase):
    """
    SQL通用模型
    """

    # 标识为抽象类，防止sqlalchemy将该类直接映射到数据库表
    __abstract__ = True

    @staticmethod
    def uid_generate() -> str:
        """
        uid生成器
        :return:
        """
        return str(ULID())

    def as_dict(self) -> dict:
        """
        将ORM模型的实例转换为字典
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
