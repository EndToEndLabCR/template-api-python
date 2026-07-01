import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.app.composition import (
    get_change_password_use_case,
    get_login_use_case,
    get_refresh_token_use_case,
    get_register_use_case,
)
from src.app.features.auth.application.dtos.auth_dto import (
    AdminLoginResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from src.app.features.auth.application.use_cases.change_password import (
    ChangePasswordUseCase,
)
from src.app.features.auth.application.use_cases.login_user import LoginUserUseCase
from src.app.features.auth.application.use_cases.refresh_token import (
    RefreshTokenUseCase,
)
from src.app.features.auth.application.use_cases.register_user import (
    RegisterUserUseCase,
)
from src.app.features.auth.domain.exceptions.auth_exceptions import (
    InvalidCredentialsError,
)
from src.app.features.user.application.dtos.user_dto import UserCreateRequest
from src.app.features.user.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError,
)
from src.app.shared.infrastructure.rate_limit.rate_limiter import limiter
from src.app.shared.infrastructure.security.token_revocation_service import (
    get_token_revocation_service,
)
from src.app.shared.presentation.auth_dependencies import get_current_user


router = APIRouter()


@router.post("/login", response_model=AdminLoginResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    login_use_case: LoginUserUseCase = Depends(get_login_use_case),
) -> AdminLoginResponse:
    """
    Authenticate user and return JWT token with user details.

    Rate limited to 10 attempts per minute per IP address to prevent brute force attacks.

    Args:
        request: FastAPI request object (required for rate limiting)
        payload: LoginRequest with email and password
        login_use_case: Injected LoginUserUseCase

    Returns:
        AdminLoginResponse with JWT token and user details

    Raises:
        401: Invalid credentials
        429: Too many requests (rate limit exceeded)
        500: Internal server error
    """
    try:
        return await login_use_case.execute(payload=payload)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


@router.post(
    "/register", response_model=AdminLoginResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: UserCreateRequest,
    register_use_case: RegisterUserUseCase = Depends(get_register_use_case),
) -> AdminLoginResponse:
    """
    Register new user and return JWT token (auto-login).

    Rate limited to 5 attempts per minute per IP address to prevent abuse.

    Public endpoint - no authentication required.
    New users default to 'viewer' role. To create admin users,
    use POST /v1/users (requires existing admin authentication).

    Args:
        request: FastAPI request object (required for rate limiting)
        payload: UserCreateRequest with email, password, displayName (role defaults to viewer)
        register_use_case: Injected RegisterUserUseCase

    Returns:
        AdminLoginResponse with JWT token and user details

    Raises:
        400: Validation failed (weak password, invalid email, etc.)
        409: Email already exists
        500: Internal server error
    """
    try:
        return await register_use_case.execute(payload=payload)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.post("/refresh", response_model=RefreshTokenResponse)
@limiter.limit("10/15minutes")
async def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    refresh_use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> RefreshTokenResponse:
    """
    Refresh access token using refresh token.

    Implements single-use refresh token rotation:
    - Returns new access token (15min TTL) AND new refresh token (7 days)
    - Old refresh token is immediately revoked and cannot be reused
    - Prevents token replay attacks

    Rate limited to 10 attempts per 15 minutes per IP address.

    Args:
        request: FastAPI request object (required for rate limiting)
        payload: RefreshTokenRequest with refresh token
        refresh_use_case: Injected RefreshTokenUseCase

    Returns:
        RefreshTokenResponse with new access and refresh tokens

    Raises:
        401: Refresh token expired or invalid
        429: Too many requests (rate limit exceeded)
        500: Internal server error
    """
    try:
        return await refresh_use_case.execute(payload=payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: dict = Depends(get_current_user),
) -> LogoutResponse:
    """
    Logout — revoke current access token.

    The current access token is immediately added to the revocation list.
    Subsequent requests with this token will receive 401.

    Requires a valid Bearer token in Authorization header.

    Returns:
        LogoutResponse with success message
    """
    jti = current_user.get("jti")
    if jti:
        token_revocation = get_token_revocation_service()
        await token_revocation.revoke_token(jti, ttl_minutes=15)
    return LogoutResponse(message="Logged out successfully")


@router.post("/change-password", response_model=ChangePasswordResponse)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
) -> ChangePasswordResponse:
    """
    Change password for the currently authenticated user.

    Requires current password verification.

    Rate limited to 5 attempts per minute per IP address.

    Args:
        request: FastAPI request object (required for rate limiting)
        payload: ChangePasswordRequest with current_password and new_password
        current_user: Authenticated user from JWT
        use_case: Injected ChangePasswordUseCase

    Returns:
        ChangePasswordResponse with success message

    Raises:
        401: Current password is incorrect or authentication invalid
        400: New password fails strength validation
    """
    try:
        return await use_case.execute(
            user_id=str(current_user["sub"]),
            payload=payload,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
