from app.features.user.application.dtos.user_dto import ForgotPasswordResponse, ResetPasswordResponse
from app.features.user.application.use_cases.forgot_password import ForgotPasswordUseCase
from app.features.user.application.use_cases.reset_password import ResetPasswordUseCase
from app.features.user.domain.repositories.user_repository import UserRepository


class PasswordService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.forgot_password_use_case = ForgotPasswordUseCase(user_repository)
        self.reset_password_use_case = ResetPasswordUseCase(user_repository)

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        return await self.forgot_password_use_case.execute(email)

    async def reset_password(self, token: str, password: str) -> ResetPasswordResponse:
        return await self.reset_password_use_case.execute(token, password)
