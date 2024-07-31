import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context

# Alembic Config object
config = context.config

# Configure logging
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

def get_engine():
    try:
        # Works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine

def get_metadata():
    # Access the metadata for migrations
    target_db = current_app.extensions['migrate'].db
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()

def process_revision_directives(context, revision, directives):
    """Callback to prevent auto-migration if no changes."""
    if getattr(config.cmd_opts, 'autogenerate', False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            logger.info('No changes in schema detected.')

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
