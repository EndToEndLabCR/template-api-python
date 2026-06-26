from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.app.features.user.application.dtos.user_dto import UserResponse
from src.app.features.user.application.exceptions.user_exception import (
    UserDoesNotExistException,
)
from src.app.features.user.application.use_cases.delete_user_by_id import (
    DeleteUserByIdUseCase,
)
from src.app.features.user.application.use_cases.get_user_by_id import (
    GetUserByIdUseCase,
)
from src.app.features.user.presentation.web.dependencies import (
    get_delete_user_use_case,
    get_user_by_id_use_case,
)

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
) -> UserResponse:
    try:
        return await use_case.execute(str(user_id))
    except UserDoesNotExistException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: UUID,
    use_case: DeleteUserByIdUseCase = Depends(get_delete_user_use_case),
):
    try:
        await use_case.execute(str(user_id))
    except UserDoesNotExistException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
