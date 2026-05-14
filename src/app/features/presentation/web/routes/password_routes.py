from fastapi import APIRouter, Depends, HTTPException, status

from src.app.features.application.dtos.user_dto import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from src.app.features.application.exceptions.password_exception import (
    ExpiredResetTokenException,
    InvalidResetTokenException,
)
from src.app.features.application.services.password_service import PasswordService
from src.app.features.presentation.web.dependencies import get_password_service


router = APIRouter()


@router.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    password_service: PasswordService = Depends(get_password_service),
):
    try:
        return await password_service.forgot_password(payload.email)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/auth/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    password_service: PasswordService = Depends(get_password_service),
):
    try:
        return await password_service.reset_password(payload.token, payload.password)

    except InvalidResetTokenException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ExpiredResetTokenException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")