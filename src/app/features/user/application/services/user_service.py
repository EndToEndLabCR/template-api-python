from app.features.user.application.dtos.user_dto import UserCreateRequest
from app.features.user.application.exceptions.auth_exception import InvalidCredentialsException
from app.features.user.application.use_cases.create_user import CreateUserUseCase
from app.features.user.application.use_cases.get_user_by_id import GetUserByIdUseCase
from app.features.user.application.use_cases.delete_user_by_id import DeleteUserByIdUseCase
from app.features.user.domain.entities.user_entity import UserEntity
from app.features.user.domain.repositories.user_repository import UserRepository
from app.features.user.domain.value_objects.email import Email
from app.features.user.domain.value_objects.password import Password


class UserService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.create_user_use_case = CreateUserUseCase(user_repository)

    async def get_user_by_id(self, user_id: str):

        use_case = GetUserByIdUseCase(self.user_repository)

        return await use_case.execute(user_id)

    async def delete_user_by_id(self, user_id: str):

        use_case = DeleteUserByIdUseCase(self.user_repository)

        return await use_case.execute(user_id)


    async def create_user(self, payload: UserCreateRequest):
        return await self.create_user_use_case.execute(payload)

    async def authenticate_user(self, email: str, password: str) -> UserEntity:

        email_vo = Email(email)
        user = await self.user_repository.find_by_email(email_vo)

        if user is None or not Password.verify(password, user.password_hash):
            raise InvalidCredentialsException()

        return user
