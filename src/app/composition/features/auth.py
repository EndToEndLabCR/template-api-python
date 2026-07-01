"""
Auth feature dependency factories — all auth use cases wired here.
"""

from fastapi import Depends

from src.app.composition.infrastructure import get_jwt_handler
from src.app.composition.repositories import get_user_repository
from src.app.features.auth.application.use_cases.change_password import (
    ChangePasswordUseCase,
)
from src.app.features.auth.application.use_cases.forgot_password import (
    ForgotPasswordUseCase,
)
from src.app.features.auth.application.use_cases.login_user import LoginUserUseCase
from src.app.features.auth.application.use_cases.refresh_token import (
    RefreshTokenUseCase,
)
from src.app.features.auth.application.use_cases.register_user import (
    RegisterUserUseCase,
)
from src.app.features.auth.application.use_cases.reset_password import (
    ResetPasswordUseCase,
)
from src.app.features.user.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from src.app.shared.infrastructure.security.jwt_handler import JWTHandler

# ── Login / Register / Refresh ────────────────────────────────────


async def get_login_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
) -> LoginUserUseCase:
    return LoginUserUseCase(repo, jwt_handler)


async def get_register_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(repo, jwt_handler)


async def get_refresh_token_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(repo, jwt_handler)


# ── Password reset ────────────────────────────────────────────────


async def get_forgot_password_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
) -> ForgotPasswordUseCase:
    return ForgotPasswordUseCase(repo)


async def get_reset_password_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(repo)


async def get_change_password_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(repo)
