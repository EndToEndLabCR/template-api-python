import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.user.domain.entities.user_entity import UserEntity
from app.features.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from app.features.user.presentation.web.dependencies import get_database_session
from app.shared.utils.jwt_util import decode_access_token

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_database_session),
) -> UserEntity:
    """
    FastAPI dependency that extracts and validates the JWT from the Authorization header.

    Returns:
        UserEntity for the authenticated user.

    Raises:
        HTTPException 401: If token is missing, invalid, expired, or user not found.
    """
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        repo = UserRepositoryImpl(session)
        user = await repo.find_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
