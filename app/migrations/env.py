import asyncio

# from logging.config import fileConfig
from alembic import context
from loguru import logger
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from app.core.models import metadata  # noqa E402
import app.modules.users.models  # noqa E402
import app.modules.workspaces.models  # noqa E402
import app.modules.channels.models  # noqa E402
import app.modules.messages.models  # noqa E402
import app.modules.files.models  # noqa E402

target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
from app.core.config import settings  # noqa E402

DATABASE_URL = str(settings.DATABASE_URL)  # Get database url

config.set_main_option("sqlalchemy.url", DATABASE_URL)  # Set database url to alembic


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
    logger.info("Alembic migrations run in offline mode.")


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_async_engine(url, poolclass=pool.NullPool, echo=True, future=True)
    logger.info("Connecting to database for online migrations...")
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    logger.info("Alembic migrations run in online mode.")


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
