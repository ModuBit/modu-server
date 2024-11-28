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

from .account import AccountRepository
from .bot import BotRepository
from .data_repository_container import get_repository, get_database
from .database import Database
from .llm import LLMProviderConfigRepository, LLMModelConfigRepository
from .message import ConversationRepository, MessageRepository, MessageSummaryRepository
from .publish import PublishConfigRepository
from .workspace import WorkspaceRepository

database: Database = get_database()
account_repository: AccountRepository = get_repository('account')
workspace_repository: WorkspaceRepository = get_repository('workspace')
llm_provider_config_repository: LLMProviderConfigRepository = get_repository('llm_provider_config')
llm_model_config_repository: LLMModelConfigRepository = get_repository('llm_model_config')
conversation_repository: ConversationRepository = get_repository('conversation')
message_repository: MessageRepository = get_repository('message')
message_summary_repository: MessageSummaryRepository = get_repository('message_summary')
bot_repository: BotRepository = get_repository('bot')
publish_config_repository: PublishConfigRepository = get_repository('publish_config')

__all__ = [
    account_repository,
    workspace_repository,
    llm_provider_config_repository,
    llm_model_config_repository,
    conversation_repository,
    message_repository,
    message_summary_repository,
]
