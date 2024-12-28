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

import os


def split_sql_statements(sql: str) -> list[str]:
    """
    将 SQL 文件内容分割为单独的语句
    处理 dollar-quoted string 和普通分号分隔的语句
    """

    statements = []
    current_statement = []
    in_dollar_quote = False

    for line in sql.splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("--"):
            # 忽略空行和注释
            continue

        if not in_dollar_quote:
            # 检查是否开始 dollar-quoted string
            if "$$" in stripped_line:
                in_dollar_quote = True
                current_statement.append(line)
            elif stripped_line.endswith(";"):
                # 检测是否是完整的 sql 语句
                current_statement.append(line)
                statements.append("\n".join(current_statement))
                current_statement = []
            else:
                current_statement.append(line)
        else:
            current_statement.append(line)
            # 检查是否结束 dollar-quoted string
            if "$$" in stripped_line:
                in_dollar_quote = False
                if stripped_line.endswith(";"):
                    # 检测是否是完整的 sql 语句
                    statements.append("\n".join(current_statement))
                    current_statement = []

    # 处理最后一个语句
    if current_statement:
        statements.append("\n".join(current_statement))

    return statements


def get_sql_statements(revision: str, action: str, db_type: str) -> list[str]:
    """
    找到指定版本的 sql 文件
    并分割为单独的 sql 语句
    """

    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取同目录同版本 sql 文件
    sql_file = os.path.join(current_dir, "versions", f"{revision}.{action}.{db_type}.sql")
    # 读取 sql 文件
    with open(sql_file, "r", encoding="utf-8") as f:
        sql = f.read()

    # 分割 SQL 语句
    # async sqlalchemy 不能一次执行多 sql
    return split_sql_statements(sql)
