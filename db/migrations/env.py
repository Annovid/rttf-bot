from logging.config import fileConfig

from alembic import context
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from db.models import Base
from utils.settings import settings

config: Config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_db_url():
    return settings.DB_URL


def process_revision_directives(context, revision, directives):
    migration_script = directives[0]
    head_revision = ScriptDirectory.from_config(
        context.config
    ).get_current_head()

    if head_revision is None:
        new_rev_id = 1
    else:
        last_rev_id = int(head_revision.lstrip("0"))
        new_rev_id = last_rev_id + 1
    migration_script.rev_id = "{0:04}".format(new_rev_id)


def run_migrations_offline() -> None:
    context.configure(
        url=get_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(get_db_url())
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
