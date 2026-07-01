#!/usr/bin/env python3
"""
Seed script to create default admin and viewer users for testing.

Idempotent — safe to run multiple times. Skips users that already exist.

Usage:
    python scripts/seed_users.py

Called automatically by scripts/start-api.sh after migrations in container.
"""

import asyncio
import os
import sys

# Ensure the project root is on the import path so that `src.*` works.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.app.config.app_config import AppConfig  # noqa: E402
from src.app.features.user.domain.entities.user_entity import UserEntity  # noqa: E402
from src.app.features.user.domain.value_objects.user_role import UserRole  # noqa: E402
from src.app.features.user.infrastructure.repositories.user_repository_impl import (  # noqa: E402
    UserRepositoryImpl,
)
from src.app.shared.domain.value_objects.email import Email  # noqa: E402
from src.app.shared.domain.value_objects.password import Password  # noqa: E402
from src.app.shared.persistence.engine_factory import close_engine, get_engine  # noqa: E402

SEED_USERS = [
    {
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "Admin123!",
        "role": UserRole.ADMIN,
    },
    {
        "email": "viewer@example.com",
        "first_name": "Viewer",
        "last_name": "User",
        "password": "Viewer123!",
        "role": UserRole.VIEWER,
    },
]


async def seed() -> None:
    """Create default users if they do not already exist."""
    AppConfig.instance()  # loads .env + YAML config
    engine = get_engine()

    async with engine.get_session() as session:
        repo = UserRepositoryImpl(session)

        for entry in SEED_USERS:
            email_vo = Email(entry["email"])

            existing = await repo.find_by_email(email_vo)
            if existing:
                print(
                    f"  SKIP  {entry['email']} ({entry['role'].value}) — already exists"
                )
                continue

            password_hash = Password(entry["password"]).hash()
            entity = UserEntity.create(
                email=entry["email"],
                first_name=entry["first_name"],
                last_name=entry["last_name"],
                password_hash=password_hash,
                role=entry["role"],
            )
            await repo.save(entity)
            print(
                f"  CREATED  {entry['email']} ({entry['role'].value})"
            )

    await close_engine()


def main() -> None:
    """Entry point — called from shell or imported."""
    print("Seeding default users...")
    asyncio.run(seed())
    print("Seeding complete.")


if __name__ == "__main__":
    main()
