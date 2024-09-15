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

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from repositories.data.account.account_models import Account
from services import account_service
from utils.errors.base_error import ErrorShowType, UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/login')


async def current_account(token: str = Depends(oauth2_scheme)) -> Account:
    """
    获取当前登录用户账号
    :param token: token
    :return: 当前登录用户账号
    """
    account = account_service.account_token_decode(token)
    if account is None:
        raise UnauthorizedError(message='Invalid Token',
                                show_type=ErrorShowType.SILENT,
                                status_code=HTTP_401_UNAUTHORIZED)
    return account


async def token_verify(token: str = Depends(oauth2_scheme)):
    """
    验证token
    :param token: token
    :return: 验证当前登录态
    """
    account_service.account_token_verify(token)
