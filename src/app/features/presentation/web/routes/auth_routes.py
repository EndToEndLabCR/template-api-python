import bcrypt
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.application.dtos.user_dto import LoginRequest, LoginResponse
from src.app.features.infrastructure.models.user_model import UserModel
from src.app.features.presentation.web.dependencies import get_database_session
from sqlalchemy import select

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_database_session)):
    # result = await session.execute(select(UserModel).where(UserModel.email == payload.username))
    # user = result.scalar_one_or_none()
    #
    # if user is None or not bcrypt.checkpw(payload.password.encode(), user.password_hash.encode()):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return LoginResponse(name=f"Alonso")
