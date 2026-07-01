"""
ChangePasswordUseCase — authenticated password change.
"""

from src.app.features.auth.application.dtos.auth_dto import (
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from src.app.features.auth.domain.exceptions.auth_exceptions import (
    InvalidCredentialsError,
)
from src.app.features.user.domain.repositories.user_repository import UserRepository
from src.app.shared.domain.value_objects.entity_id import EntityId
from src.app.shared.domain.value_objects.password import Password
from src.app.shared.logging import BusinessLogger, get_logger


class ChangePasswordUseCase:
    """Use case for authenticated users to change their password."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self,
        user_id: str,
        payload: ChangePasswordRequest,
    ) -> ChangePasswordResponse:
        """
        Change password for authenticated user.

        Args:
            user_id: ID of the authenticated user (from JWT)
            payload: ChangePasswordRequest with current and new passwords

        Returns:
            ChangePasswordResponse with success message

        Raises:
            InvalidCredentialsError: If current password is wrong
            ValueError: If new password fails validation
        """
        log = BusinessLogger(get_logger(__name__), user_id=user_id)

        try:
            entity_id = EntityId.from_string(user_id)
            user_entity = await self.user_repository.find_by_id(entity_id)

            if not user_entity:
                log.warning(
                    "Change password attempt for non-existent user",
                    event_type="auth.change_password.user_not_found",
                )
                raise InvalidCredentialsError("User not found")

            # Verify current password
            if not Password.verify(payload.current_password, user_entity.password_hash):
                log.warning(
                    "Change password failed — current password incorrect",
                    event_type="auth.change_password.invalid_current",
                )
                raise InvalidCredentialsError("Current password is incorrect")

            # Hash and set new password
            new_password_hash = Password(payload.new_password).hash()
            user_entity.update_details(password_hash=new_password_hash)
            await self.user_repository.update(user_entity)

            log.info(
                "Password changed successfully",
                event_type="auth.change_password.success",
            )
            return ChangePasswordResponse(message="Password changed successfully")

        except (InvalidCredentialsError, ValueError):
            raise
        except Exception as e:
            log.error(
                "Unexpected error in ChangePasswordUseCase",
                error=e,
                error_type="auth.change_password.unexpected_error",
            )
            raise
