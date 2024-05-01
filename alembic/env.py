from logging.config import fileConfig
from pathlib import Path

import sqlalchemy
from loguru import logger
from sqlalchemy import engine_from_config, pool, text
from sqlmodel import SQLModel, create_engine

from alembic import context
from magic_circle.config import config as mconfig
from magic_circle.repo import *  # noqa

for dir in Path("./magic_circle").glob("./*"):
    if not dir.is_dir():
        continue

    try:
        exec(f"from magic_circle.{dir.name}.db import *")
    except Exception:
        pass

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    db_url, db_name = mconfig.DB_URL.rsplit("/", 1)
    db_url = db_url.replace("+asyncmy", "")
    with create_engine(db_url).connect() as c:
        try:
            c.execute(text(f"create database {db_name};"))
        except Exception as e:
            if "database exists" not in str(e):
                logger.error(e)

    def process_revision_directives(context, revision, directives):
        if config.cmd_opts.autogenerate:
            script = directives[0]

        if script.upgrade_ops.is_empty():
            directives[:] = []
            print("No changes in schema detected.")

    # inject url
    section = config.get_section(config.config_ini_section)
    section["sqlalchemy.url"] = db_url + "/" + db_name
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # detect changes on enum
    def my_compare_type(
        context, inspected_column, metadata_column, inspected_type, metadata_type
    ):
        # return False if the metadata_type is the same as the inspected_type
        # or None to allow the default implementation to compare these
        # types. a return value of True means the two types do not
        # match and should result in a type change operation.

        if isinstance(inspected_type, sqlalchemy.Enum) and isinstance(
            metadata_type, sqlalchemy.Enum
        ):
            inspected_enum_values = set(inspected_type.enums)
            metadata_enum_values = set(metadata_type.enums)
            return inspected_enum_values != metadata_enum_values

        return None

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            compare_type=my_compare_type,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
