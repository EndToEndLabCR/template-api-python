from app.features.user.application.dtos.user_dto import UserCreateRequest, UserResponse
from app.features.user.application.dtos.user_dto_mapper import map_create_request_to_entity, map_entity_to_dto_user
from app.features.user.application.exceptions.user_exception import UserAlreadyExistsException
from app.features.user.domain.repositories.user_repository import UserRepository
from app.features.user.domain.value_objects.password import Password
from app.shared.utils.log_util import log


class CreateUserUseCase:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, payload: UserCreateRequest) -> UserResponse:
        try:
            # Validate and hash password via domain value object
            password_vo = Password(payload.password)
            password_hash = password_vo.hash()

            new_user_entity = map_create_request_to_entity(payload, password_hash)

            existing_user = await self.user_repository.find_by_email(new_user_entity.email)

            if existing_user:
                log.warning(f"Duplicate user creation attempt with email: {new_user_entity.email}")
                raise UserAlreadyExistsException(str(new_user_entity.email))

            created_user = await self.user_repository.save(new_user_entity)

            response_dto = map_entity_to_dto_user(created_user)

            log.info(f"User created successfully: {created_user.id}")
            return response_dto

        except (ValueError, UserAlreadyExistsException):
            raise
        except Exception as e:
            log.error(f"Unexpected error in CreateUserUseCase: {str(e)}")
            raise