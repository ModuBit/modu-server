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

from logging.config import fileConfig
import logging

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from config import app_config

logger = logging.getLogger("alembic")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

def get_url():
    """
    从应用配置中获取数据库连接字符串
    """
    data = app_config.repository.data
    type = data.type
    if type == "postgres":
        url = f"postgresql+asyncpg://{data.postgres.username}:{data.postgres.password}@{data.postgres.host}:{data.postgres.port}/{data.postgres.database}"
        logger.info(f"Database URL: postgresql+asyncpg://{data.postgres.username}@{data.postgres.host}:{data.postgres.port}/{data.postgres.database}")
        return url
    else:
        raise ValueError(f"Unsupported database type: {type}")


def do_run_migrations(connection: Connection) -> None:
    logger.info("Starting migrations")
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()
    logger.info("Migrations completed")


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    logger.info("Starting async migrations")
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = create_async_engine(configuration["sqlalchemy.url"])
    logger.info("Created async engine")

    async with connectable.connect() as connection:
        logger.info("Running migrations")
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()
    logger.info("Disposed engine")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    """
    logger.info("Running migrations in offline mode")
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
    logger.info("Offline migrations completed")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    """
    logger.info("Running migrations in online mode")
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
