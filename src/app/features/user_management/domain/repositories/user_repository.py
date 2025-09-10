from abc import abstractmethod
from typing import Optional, AsyncIterator

from src.app.features.user_management.domain.entities.user_enums import UserRole, UserStatus
from src.app.features.user_management.domain.entities.user_entity import UserEntity
from src.app.features.user_management.domain.value_objects.email import Email
from src.app.features.user_management.domain.value_objects.user_id import UserId
from src.shared.domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity, UserId]):
    """User repository interface"""

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        """
        Find a user by their email address.

        :param email: The email to search for.
        :return: The user entity or None if not found.
        """
        pass

    @abstractmethod
    async def find_by_role(self, role: UserRole, limit: Optional[int] = None, offset: Optional[int] = None) -> \
            AsyncIterator[UserEntity]:
        """
        Find users by their role.

        :param role: The user role to filter by.
        :param limit: Optional limit for pagination.
        :param offset: Optional offset for pagination.
        :return: An asynchronous iterator of user entities.
        """
        pass

    @abstractmethod
    async def find_by_status(self, status: UserStatus, limit: Optional[int] = None, offset: Optional[int] = None) -> \
            AsyncIterator[UserEntity]:
        """
        Find users by their status.

        :param status: The user status to filter by.
        :param limit: Optional limit for pagination.
        :param offset: Optional offset for pagination.
        :return: An asynchronous iterator of user entities.
        """
        pass

    @abstractmethod
    async def email_exists(self, email: Email, exclude_id: Optional[UserId] = None) -> bool:
        """
        Check if an email already exists in the repository.

        :param email: The email to check.
        :param exclude_id: Optional user ID to exclude from the check.
        :return: True if the email exists, otherwise False.
        """
        pass
