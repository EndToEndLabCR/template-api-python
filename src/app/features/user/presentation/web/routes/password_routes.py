from fastapi import APIRouter, Depends, HTTPException, status

from app.features.user.application.dtos.user_dto import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.features.user.application.exceptions.password_exception import (
    ExpiredResetTokenException,
    InvalidResetTokenException,
)
from app.features.user.application.exceptions.user_exception import UserEmailNotFoundException
from app.features.user.application.services.password_service import PasswordService
from app.features.user.presentation.web.dependencies import get_password_service


router = APIRouter()


@router.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    password_service: PasswordService = Depends(get_password_service),
):
    try:
        return await password_service.forgot_password(payload.email)

    except UserEmailNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

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