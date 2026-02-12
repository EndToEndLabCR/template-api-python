from src.app.features.application.dtos.user_dto import UserCreateRequest, UserResponse
from src.app.features.application.dtos.user_dto_mapper import map_create_request_to_entity, map_entity_to_dto_user
from src.app.features.application.exceptions.user_exception import UserAlreadyExistsException
from src.app.features.domain.repositories.user_repository import UserRepository
from src.shared.utils.log_util import log


class CreateUserUseCase:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, payload: UserCreateRequest) -> UserResponse:
        try:
            # 1) Normalizar email (evita duplicados por mayúsculas/espacios)
            email = str(payload.email).lower().strip()

            # 2) Validar duplicado
            #    (necesita que el repositorio implemente find_by_email o exists_by_email)
            existing_user = await self.user_repository.find_by_email(email)

            if existing_user:
                log.warning(f"Duplicate user creation attempt with email: {email}")
                raise UserAlreadyExistsException(email)

            # 3) DTO -> Entity (sin password; la entity no lo maneja)
            new_user_entity = map_create_request_to_entity(payload)

            # 4) Guardar (repo persiste y maneja password/hash en infraestructura)
            created_user = await self.user_repository.create_user(new_user_entity, payload.password)

            # 5) Entity -> Response DTO
            response_dto = map_entity_to_dto_user(created_user)

            return response_dto

        except ValueError as e:
            raise
        except UserAlreadyExistsException as e:
            raise
        except Exception as e:
            raise