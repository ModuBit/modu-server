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

from datetime import datetime, timedelta

from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from utils.errors.base_error import UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    密码加密
    :param password: 密码
    :return: HASH后的密码
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    密码验证
    :param password: 密码
    :param password_hash: HASH后的密码
    :return: True / False
    """
    return pwd_context.verify(password, password_hash)


def jose_encode(payload: dict, secret: str, algorithm: str, expires_minutes: float):
    """
    jose 令牌
    :param payload: 负载
    :param secret: 密钥
    :param algorithm: 算法
    :param expires_minutes: 过期时间
    :return: 令牌
    """
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt


def jose_decode(token: str, secret: str, algorithm: str):
    """
    jose 令牌
    :param token: jwt token
    :param secret: 密钥
    :param algorithm: 算法
    :return: 负载
    """
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except ExpiredSignatureError:
        raise UnauthorizedError(
            message="Token has expired.", status_code=HTTP_401_UNAUTHORIZED
        )
    except JWTError:
        raise UnauthorizedError(
            message="Invalid Token.", status_code=HTTP_401_UNAUTHORIZED
        )
