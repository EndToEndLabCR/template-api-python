"""
Composition root — public API for all dependency injection factories.

Sub-modules contain the actual implementations:
  - infrastructure.py: DB session, JWT handler
  - repositories.py:   Shared repository factories
  - features/auth.py:  Auth use case factories (login, register, refresh, password reset)
  - features/users.py: User use case factories (CRUD only)
"""

from src.app.composition.features.auth import (
    get_forgot_password_use_case,
    get_login_use_case,
    get_refresh_token_use_case,
    get_register_use_case,
    get_reset_password_use_case,
)
from src.app.composition.features.users import (
    get_create_user_use_case,
    get_delete_user_use_case,
    get_list_users_use_case,
    get_update_user_use_case,
    get_user_by_id_use_case,
)
from src.app.composition.infrastructure import (
    get_database_session,
    get_jwt_handler,
)
from src.app.composition.repositories import get_user_repository

__all__ = [
    "get_database_session",
    "get_jwt_handler",
    "get_user_repository",
    # Auth
    "get_login_use_case",
    "get_register_use_case",
    "get_refresh_token_use_case",
    "get_forgot_password_use_case",
    "get_reset_password_use_case",
    # User
    "get_create_user_use_case",
    "get_user_by_id_use_case",
    "get_update_user_use_case",
    "get_list_users_use_case",
    "get_delete_user_use_case",
]
