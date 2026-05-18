import hashlib
import secrets
from datetime import datetime, timedelta

from src.app.config.app_config import AppConfig
from src.app.features.application.dtos.user_dto import ForgotPasswordResponse
from src.app.features.domain.repositories.user_repository import UserRepository
from src.app.features.domain.value_objects.email import Email
from src.shared.utils.log_util import log


class ForgotPasswordUseCase:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.token_expire_minutes = int(
            AppConfig.instance().get_config("security.password_reset_token_expire_minutes", 1)
        )

    async def execute(self, email: str) -> ForgotPasswordResponse:
        try:
            email_vo = Email(email.lower().strip())
            user_entity = await self.user_repository.find_by_email(email_vo)

            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            expires_at = datetime.now() + timedelta(minutes=self.token_expire_minutes)

            if user_entity:
                user_entity.password_reset_token_hash = token_hash
                user_entity.password_reset_expires_at = expires_at
                user_entity.mark_as_updated()
                await self.user_repository.update(user_entity)
                log.info(f"Password reset token generated for email: {email}")
            else:
                log.info(f"Password reset requested for non-existent email: {email}")

            return ForgotPasswordResponse(
                message="Password reset link sent to the frontend",
                token=raw_token,
            )

        except ValueError:
            raise
        except Exception as e:
            log.error(f"Unexpected error in ForgotPasswordUseCase: {str(e)}")
            raise
