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

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from dependency_injector.wiring import inject, Provide
from app_container import AppContainer
from services.account import AccountService

router = APIRouter()


@router.post("/login")
@inject
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    accountService: AccountService = Depends(
        Provide[AppContainer.serviceContainer.accountContainer.accountService]
    ),
):
    return accountService.authenticate(form_data.username, form_data.password)


@router.get("/logout")
def logout():
    return
