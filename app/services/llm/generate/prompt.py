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
from langchain_core.prompts import PromptTemplate

DEFAULT_SUMMARIZER_TEMPLATE = """逐步总结提供的对话内容，增加到之前的摘要中，并返回新的摘要。

>>> EXAMPLE
当前摘要：
人类问AI对人工智能的看法。AI认为人工智能是一种积极的力量。

新的对话内容：
Human: 你为什么认为人工智能是一种积极的力量？
AI: 因为人工智能将帮助人类发挥他们的全部潜力。

新摘要：
人类问AI对人工智能的看法。AI认为人工智能是一种积极的力量，因为它将帮助人类发挥他们的全部潜力。
<<< END OF EXAMPLE

当前摘要：
{summary}

新的对话内容：
{new_message}

新摘要：
"""

SUMMARY_PROMPT = PromptTemplate(
    input_variables=["summary", "new_message"], template=DEFAULT_SUMMARIZER_TEMPLATE
)
