import hashlib

from src.app.features.auth.application.dtos.auth_dto import ResetPasswordResponse
from src.app.features.auth.domain.exceptions.auth_exceptions import (
    ExpiredResetTokenException,
    InvalidResetTokenException,
)
from src.app.features.user.domain.repositories.user_repository import UserRepository
from src.app.shared.domain.value_objects.password import Password
from src.app.shared.utils.log_util import log


class ResetPasswordUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, token: str, new_password: str) -> ResetPasswordResponse:
        try:
            # Validate password strength via domain value object
            password_vo = Password(new_password)
            new_password_hash = password_vo.hash()

            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

            # Verify the token exists at all
            user_entity = await self.user_repository.find_by_reset_token_hash(
                token_hash
            )
            if user_entity is None:
                log.warning("Reset password attempted with invalid token hash.")
                raise InvalidResetTokenException()

            # Atomically reset password if token is still valid (not expired)
            success = await self.user_repository.reset_password(
                token_hash, new_password_hash
            )
            if not success:
                log.warning("Reset password failed — token expired or already consumed.")
                raise ExpiredResetTokenException()

            log.info(f"Password reset successfully for user: {user_entity.id}")

            return ResetPasswordResponse(message="Password has been reset successfully")

        except (InvalidResetTokenException, ExpiredResetTokenException):
            raise
        except Exception as e:
            log.error(f"Unexpected error in ResetPasswordUseCase: {str(e)}")
            raise
