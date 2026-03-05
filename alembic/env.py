import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

# -------------------------------------------------------------------------
# Asegura que Alembic pueda importar la app (app.*)
# -------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.getcwd()))

# -------------------------------------------------------------------------
# Imports de tu aplicación
# -------------------------------------------------------------------------
from app.db.base import Base
from app.db.session import engine
import app.models  # 🔥 registra TODOS los modelos

# -------------------------------------------------------------------------
# Configuración base de Alembic
# -------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de TODOS los modelos
target_metadata = Base.metadata


# -------------------------------------------------------------------------
# Migraciones OFFLINE
# -------------------------------------------------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------------------------
# Migraciones ONLINE
# -------------------------------------------------------------------------
def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------------------------------
# Selector de modo
# -------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()