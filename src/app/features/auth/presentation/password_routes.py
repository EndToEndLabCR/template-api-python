from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.app.composition import (
    get_forgot_password_use_case,
    get_reset_password_use_case,
)
from src.app.features.auth.application.dtos.auth_dto import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from src.app.features.auth.application.use_cases.forgot_password import (
    ForgotPasswordUseCase,
)
from src.app.features.auth.application.use_cases.reset_password import (
    ResetPasswordUseCase,
)
from src.app.features.auth.domain.exceptions.auth_exceptions import (
    ExpiredResetTokenException,
    InvalidResetTokenException,
)
from src.app.shared.infrastructure.rate_limit.rate_limiter import limiter

router = APIRouter()


@router.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    use_case: ForgotPasswordUseCase = Depends(get_forgot_password_use_case),
):
    """Request a password reset link. Always returns success to prevent email enumeration."""
    try:
        return await use_case.execute(payload.email)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/auth/reset-password", response_model=ResetPasswordResponse)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    use_case: ResetPasswordUseCase = Depends(get_reset_password_use_case),
):
    try:
        return await use_case.execute(payload.token, payload.password)

    except InvalidResetTokenException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except ExpiredResetTokenException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
