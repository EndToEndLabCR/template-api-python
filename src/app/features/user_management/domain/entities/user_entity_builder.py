from src.app.features.user_management.domain.entities.user_entity import UserEntity
from src.app.features.user_management.domain.entities.user_enums import UserRole
from src.app.features.user_management.domain.value_objects.email import Email
from src.app.features.user_management.domain.value_objects.phone_number import PhoneNumber
from src.app.features.user_management.domain.value_objects.user_id import UserId


class UserEntityBuilder:
    """
    Builder for creating a UserEntity object.
    """

    def __init__(self):
        self._user_entity = UserEntity(
            id=UserId.generate(),
            first_name="",
            last_name="",
            email=Email("test@gmail.com"),
            role=UserRole.ADMIN,
            password_hash=None,
        )

    def with_id(self, user_id):
        self._user_entity.id = UserId(user_id)
        return self

    def with_first_name(self, first_name: str):
        self._user_entity.first_name = first_name
        return self

    def with_last_name(self, last_name: str):
        self._user_entity.last_name = last_name
        return self

    def with_email(self, email):
        self._user_entity.email = Email(email)
        return self

    def with_role(self, role):
        self._user_entity.role = UserRole(role)
        return self

    def with_password_hash(self, password_hash):
        self._user_entity.password_hash = password_hash
        return self

    def build(self) -> UserEntity:
        return self._user_entity
