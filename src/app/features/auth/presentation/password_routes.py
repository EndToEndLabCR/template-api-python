from fastapi import APIRouter, Depends, HTTPException, status

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
from src.app.features.user.application.exceptions.user_exception import (
    UserEmailNotFoundException,
)

router = APIRouter()


@router.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    use_case: ForgotPasswordUseCase = Depends(get_forgot_password_use_case),
):
    try:
        return await use_case.execute(payload.email)

    except UserEmailNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/auth/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
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
