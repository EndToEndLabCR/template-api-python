from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.app.features.application.dtos.user_dto import UserResponse
from src.app.features.application.exceptions.user_exception import UserDoesNotExistException
from src.app.features.application.services.user_service import UserService
from src.app.features.presentation.web.dependencies import get_user_service

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: UUID, user_service: UserService = Depends(get_user_service)) -> UserResponse:
    # """
    # Get a user by their ID.
    #
    # Args:
    #     user_id (UUID): The user's unique identifier.
    #
    # Returns:
    #     UserResponse: The user's details.
    # """

    try:
        user_result = await user_service.get_user_by_id(str(user_id))

        return user_result

    except UserDoesNotExistException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(user_id: UUID, user_service: UserService = Depends(get_user_service)):
    # """
    # Delete a user by their ID.
    #
    # Args:
    #     user_id (UUID): The user's unique identifier.
    #
    # Returns:
    #     None
    # """

    try:
        await user_service.delete_user_by_id(str(user_id))

    except UserDoesNotExistException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
