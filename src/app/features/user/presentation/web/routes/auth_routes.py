from fastapi import APIRouter, HTTPException, status, Depends

from app.features.user.application.dtos.user_dto import LoginRequest, LoginResponse
from app.features.user.application.exceptions.auth_exception import InvalidCredentialsException
from app.features.user.application.services.user_service import UserService
from app.features.user.presentation.web.dependencies import get_user_service
from app.shared.utils.jwt_util import create_access_token

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, user_service: UserService = Depends(get_user_service)):
    try:
        user = await user_service.authenticate_user(email=payload.email, password=payload.password)

        access_token = create_access_token(data={"sub": str(user.id)})

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            name=user.first_name,
        )

    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
