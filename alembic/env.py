from logging.config import fileConfig
import asyncio


from sqlalchemy import pool
import importlib
import pkgutil


from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.app.config.app_config import AppConfig
from src.shared.domain.models.base_model import Base

# Alembic Config object, which provides access to the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Automatically import all models, so they're registered with SQLAlchemy metadata
def import_all_models():
    """Automatically import all models from the project to register them with Base.metadata"""
    # Start with the src directory
    package_dir = "src"
    for (_, name, _) in pkgutil.iter_modules([package_dir]):
        # Recursively walk through all modules in src
        module_path = f"{package_dir}.{name}"
        walk_modules(module_path)

    # Uncomment and print Base.metadata.tables to debug
    # print("Discovered models:", Base.metadata.tables.keys())


def walk_modules(package_name):
    """Recursively walk through modules in a package to import all modules"""
    try:
        package = importlib.import_module(package_name)
        if hasattr(package, "__path__"):
            # It's a package, walk through its modules
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
                if "model" in name.lower() or is_pkg:  # Import directly if it's a model, or walk if it's a package
                    try:
                        importlib.import_module(name)
                        if is_pkg:
                            walk_modules(name)
                    except ImportError as e:
                        # Optional: Log error but continue
                        print(f"Error importing {name}: {e}")
    except ImportError:
        # Package doesn't exist, ignore
        pass


# Import all models to register them with Base.metadata
import_all_models()

# Import specific models you definitely need to ensure they're loaded
# This is a safeguard in case the automatic discovery misses something
# from src.app.features.user_management.infrastructure.persistence.postgres.models.user_model import UserModel
# Add any other critical model imports here

# Add your models' metadata object here for 'autogenerate' support.
target_metadata = Base.metadata

# Dynamically load database URL
postgres_config = AppConfig.instance().get_config("postgres", {})

# Build the database URL for async operations
# Assuming your config has the necessary database connection details
db_host = postgres_config.get("host", "")
db_port = postgres_config.get("port", 5432)
db_name = postgres_config.get("dbname", "")
db_user = postgres_config.get("username", "")
db_password = postgres_config.get("password", "")

# Create async database URL
async_db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Set the sqlalchemy.url for async operations
config.set_main_option("sqlalchemy.url", async_db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure context and run migrations."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()