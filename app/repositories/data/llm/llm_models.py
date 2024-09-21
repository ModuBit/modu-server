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

from utils import json

from pydantic import BaseModel

from config import app_config
from utils.crypto import composition
from utils.pydantic import default_model_config


class LLMProviderConfig(BaseModel):
    """
    LLM Provider 配置
    """

    uid: str | None = None
    """Provider config UID"""

    workspace_uid: str
    """空间UID"""

    provider_name: str
    """Provider Name"""

    provider_credential: dict | str
    """Provider 凭证"""

    # 定义配置
    model_config = default_model_config()

    def encrypt_credential(self):
        if isinstance(self.provider_credential, str):
            return self

        self.provider_credential = composition.encrypt_str(app_config.security.secret, self.workspace_uid,
                                                           json.dumps(self.provider_credential))
        return self

    def decrypt_credential(self):
        if isinstance(self.provider_credential, dict):
            return self

        self.provider_credential = json.loads(composition.decrypt_str(app_config.security.secret, self.workspace_uid,
                                                                      self.provider_credential))
        return self


class LLMModelConfig(BaseModel):
    """
    LLM Model 配置
    """

    provider_name: str
    """Provider Name"""

    model_name: str
    """Model Name"""

    model_parameters: dict
    """Model 参数"""

    # 定义配置
    model_config = default_model_config({
        # 设置 protected_namespaces
        # UserWarning: Field "model_name" has conflict with protected namespace "model_".
        # UserWarning: Field "model_parameters" has conflict with protected namespace "model_".
        "protected_namespaces": ("_", "__")
    })
