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

from fastapi import APIRouter
from loguru import logger

from config import app_config
from utils.pydantic import CamelCaseJSONResponse

router = APIRouter()


@logger.catch()
@router.get("/profile", response_class=CamelCaseJSONResponse)
async def profile():
    """
    系统信息
    """
    return {"app_info": app_config.get("app", {})}
