import hashlib
from datetime import datetime

import bcrypt

from app.features.user.application.dtos.user_dto import ResetPasswordResponse
from app.features.user.application.exceptions.password_exception import (
    ExpiredResetTokenException,
    InvalidResetTokenException,
)
from app.features.user.domain.repositories.user_repository import UserRepository
from app.shared.utils.log_util import log


class ResetPasswordUseCase:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, token: str, new_password: str) -> ResetPasswordResponse:
        try:
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

            user_entity = await self.user_repository.find_by_reset_token_hash(token_hash)

            if user_entity is None:
                log.warning("Reset password attempted with invalid token hash.")
                raise InvalidResetTokenException()

            if user_entity.password_reset_expires_at is None or datetime.now() > user_entity.password_reset_expires_at:
                log.warning("Reset password attempted with expired token.")
                raise ExpiredResetTokenException()

            new_password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            user_entity.password_hash = new_password_hash
            user_entity.password_reset_token_hash = None
            user_entity.password_reset_expires_at = None
            user_entity.mark_as_updated()
            await self.user_repository.update(user_entity)

            log.info(f"Password reset successfully for user: {user_entity.id}")

            return ResetPasswordResponse(message="Password has been reset successfully")

        except (InvalidResetTokenException, ExpiredResetTokenException):
            raise
        except Exception as e:
            log.error(f"Unexpected error in ResetPasswordUseCase: {str(e)}")
            raise
