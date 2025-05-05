import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, from .ini
config = context.config

# interpret the config file for Python logging
fileConfig(config.config_file_name)

# add your model's MetaData object here
# make sure the app's parent folder is on PYTHONPATH
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db import engine   # SQLAlchemy engine
from app.models.user import Base as UserBase
# If you have other models, import the Base.meta here too:
# from app.models.env import Base as EnvBase
# metadata = UserBase.metadata  # if only users
from app.models import Base     # or aggregate: Base = UserBase.metadata

target_metadata = UserBase.metadata     # or Base.metadata if aggregated


def run_migrations_online():
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,      # detect type changes
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Offline mode not supported")
else:
    run_migrations_online()
