from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.composition import (
    get_create_user_use_case,
    get_delete_user_use_case,
    get_list_users_use_case,
    get_update_user_use_case,
    get_user_by_id_use_case,
)
from src.app.shared.presentation.auth_dependencies import (
    get_current_user,
    require_admin,
)
from src.app.features.user.application.dtos.user_dto import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.app.shared.application.dtos.pagination_dto import PaginatedResponse
from src.app.features.user.application.use_cases.create_user import (
    CreateUserUseCase,
)
from src.app.features.user.application.use_cases.delete_user_by_id import (
    DeleteUserByIdUseCase,
)
from src.app.features.user.application.use_cases.get_user_by_id import (
    GetUserByIdUseCase,
)
from src.app.features.user.application.use_cases.list_users import (
    ListUsersUseCase,
)
from src.app.features.user.application.use_cases.update_user_by_id import (
    UpdateUserByIdUseCase,
)
from src.app.features.user.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    current_user: dict[str, Any] = Depends(require_admin),
) -> UserResponse:
    try:
        return await use_case.execute(payload)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PaginatedResponse[UserResponse]:
    return await use_case.execute(skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    try:
        return await use_case.execute(str(current_user["sub"]))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UserResponse:
    try:
        return await use_case.execute(str(user_id))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    use_case: UpdateUserByIdUseCase = Depends(get_update_user_use_case),
    current_user: dict[str, Any] = Depends(require_admin),
) -> UserResponse:
    try:
        return await use_case.execute(str(user_id), payload)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    use_case: DeleteUserByIdUseCase = Depends(get_delete_user_use_case),
    current_user: dict[str, Any] = Depends(require_admin),
):
    try:
        await use_case.execute(str(user_id))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
