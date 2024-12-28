"""init

Revision ID: 2024122816
Revises: 
Create Date: 2024-12-28 16:36:54.258151

"""

import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from config import app_config
from migration.utils import get_sql_statements

import logging

logger = logging.getLogger("alembic")

# revision identifiers, used by Alembic.
revision: str = "2024122816"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

data_type = app_config.repository.data.type


def upgrade() -> None:
    # 分割 SQL 语句
    # async sqlalchemy 不能一次执行多 sql
    statements = get_sql_statements(revision, "upgrade", data_type)

    # 获取数据库连接
    connection = op.get_bind()

    # 直接执行所有语句
    for stmt in statements:
        if stmt.strip():
            logger.info(f"Executing statement: {stmt}")
            connection.execute(sa.text(stmt))


def downgrade() -> None:
    pass
