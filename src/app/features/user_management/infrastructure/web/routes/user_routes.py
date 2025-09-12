from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.app.features.user_management.application.dtos.user_dto import UserResponse, CreateUserRequest, UpdateUserRequest
from src.app.features.user_management.application.exceptions.user_exceptions import (
    UserDoesNotExistException,
    UserAlreadyExistsException,
)
from src.app.features.user_management.application.services.user_service import UserService
from src.app.features.user_management.infrastructure.web.dependencies import get_user_service
from src.shared.utils.log_util import log

# Define the user management router
router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(create_user_dto: CreateUserRequest, user_service: UserService = Depends(get_user_service)):
    """
    Create a new user.

    Args:
        create_user_dto (CreateUserRequest): The user creation data.
        user_service (UserService): The user service.

    Returns:
        UserResponse: The created user's details.

    Raises:
        HTTPException: If there is a validation error, user already exists, or an unexpected error occurs.
    """
    log.info(f"Creating user with data: {create_user_dto}")

    try:
        result = await user_service.create_user(create_user_dto)
        log.info(f"User created successfully: {result}")

        return result

    except ValueError as e:
        log.warning(f"[Create User] Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserAlreadyExistsException as e:
        log.warning(f"[Create User] User already exists: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User already exists: {str(e)}")
    except Exception as e:
        log.error(f"[Create User] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: UUID, user_service: UserService = Depends(get_user_service)):
    """
    Get a user by their ID.

    Args:
        user_id (UUID): The user's unique identifier.
        user_service (UserService): The user service.

    Returns:
        UserResponse: The user's details.

    Raises:
        HTTPException: If the user does not exist or an unexpected error occurs.
    """
    log.info(f"Fetching user by ID: {user_id}")

    try:
        result = await user_service.get_user_by_id(str(user_id))
        log.info(f"User fetched successfully: {result}")

        return result

    except ValueError as e:
        log.warning(f"[Get User by ID] Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserDoesNotExistException as e:
        log.warning(f"[Get User by ID] User not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log.error(f"[Get User by ID] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=List[UserResponse])
async def get_all_users(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
                        user_service: UserService = Depends(get_user_service)):
    """
    Get a paginated list of all users.

    Args:
        page (int): The page number (default: 1, minimum: 1).
        page_size (int): The number of users per page (default: 10, range: 1-100).
        user_service (UserService): The user service.

    Returns:
        List[UserResponse]: A list of user details.

    Raises:
        HTTPException: If an unexpected error occurs.
    """
    log.info(f"Fetching all users: page={page}, page_size={page_size}")

    try:
        result = await user_service.get_all_users(limit=page_size, offset=(page - 1) * page_size)
        log.info(f"{len(result)} users fetched successfully")

        return result

    except Exception as e:
        log.error(f"[Get All Users] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, update_user_dto: UpdateUserRequest,
                      user_service: UserService = Depends(get_user_service)):
    """
    Update a user's details.

    Args:
        user_id (UUID): The user's unique identifier.
        update_user_dto (UpdateUserRequest): The updated user data.
        user_service (UserService): The user service.

    Returns:
        UserResponse: The updated user's details.

    Raises:
        HTTPException: If the user does not exist, validation fails, or an unexpected error occurs.
    """
    log.info(f"Updating user {user_id} with data: {update_user_dto}")

    try:
        result = await user_service.update_user(str(user_id), update_user_dto)
        log.info(f"User updated successfully: {result}")

        return result

    except ValueError as e:
        log.warning(f"[Update User] Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserDoesNotExistException as e:
        log.warning(f"[Update User] User not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log.error(f"[Update User] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, user_service: UserService = Depends(get_user_service)):
    """
    Delete a user by their ID.

    Args:
        user_id (UUID): The user's unique identifier.
        user_service (UserService): The user service.

    Returns:
        None: Indicates successful deletion.

    Raises:
        HTTPException: If the user does not exist or an unexpected error occurs.
    """
    log.info(f"Deleting user by ID: {user_id}")

    try:
        await user_service.delete_user(str(user_id))
        log.info(f"User deleted successfully: {user_id}")

        return None

    except ValueError as e:
        log.warning(f"[Delete User] Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserDoesNotExistException as e:
        log.warning(f"[Delete User] User not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log.error(f"[Delete User] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
