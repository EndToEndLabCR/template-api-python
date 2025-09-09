from src.app.features.user_management.application.dtos.user_dto import CreateUserRequest, UserResponse
from src.app.features.user_management.application.exceptions.user_exceptions import UserAlreadyExistsException
from src.app.features.user_management.application.dtos.user_dto_mapper import map_dto_to_entity_user, \
    map_entity_to_dto_user
from src.app.features.user_management.domain.repositories.user_repository import UserRepository
from src.app.features.user_management.domain.value_objects.email import Email
from src.shared.utils.log_util import log


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, create_user_request: CreateUserRequest) -> UserResponse:
        log.info(f"Starting user creation process for email: {create_user_request.email}")

        try:
            log.debug(f"Checking if user with email {create_user_request.email} already exists")
            user_email = Email(str(create_user_request.email))
            existing_user = await self.user_repository.find_by_email(user_email)

            if existing_user:
                log.warning(f"User creation failed: User with email {create_user_request.email} already exists")
                raise UserAlreadyExistsException(f"User with email {create_user_request.email} already exists.")

            log.debug("User email is unique, proceeding with user creation")
            user_entity = map_dto_to_entity_user(create_user_request)
            log.debug(f"User entity created for {create_user_request.first_name} {create_user_request.last_name}")

            log.info(f"Saving user to repository: {create_user_request.email}")
            created_user = await self.user_repository.save(user_entity)

            log.info(f"User successfully created with ID: {created_user.id}")
            user_response_dto = map_entity_to_dto_user(created_user)
            log.info(f"User creation process completed successfully for email: {create_user_request.email}")

            return user_response_dto

        except UserAlreadyExistsException:
            log.error(f"User creation failed: User already exists with email {create_user_request.email}")
            raise
        except Exception as e:
            log.error(f"Unexpected error during user creation for email {create_user_request.email}: {str(e)}")
            raise
