from typing import List, Optional, AsyncIterator

from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.app.features.user_management.domain.entities.user_entity import UserEntity
from src.app.features.user_management.domain.entities.user_enums import UserStatus, UserRole
from src.app.features.user_management.domain.repositories.user_repository import UserRepository
from src.app.features.user_management.domain.value_objects.email import Email
from src.app.features.user_management.domain.value_objects.user_id import UserId
from src.app.features.user_management.infrastructure.databases.postgres.models.user_model import UserModel
from src.shared.utils.log_util import log
from src.shared.utils.retry_decorator import retry_read_operation, retry_write_operation, retry_critical_operation


class UserRepositoryImpl(UserRepository):
    """
    Implementation of the UserRepository interface using SQLAlchemy and UserModel.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the UserRepositoryImpl with a SQLAlchemy AsyncSession.

        Args:
            session (AsyncSession): The SQLAlchemy session to use for database operations.
        """
        self.session = session

    @retry_read_operation()
    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        """
        Find a user by their email address.

        Args:
            email (Email): The email address to search for.

        Returns:
            Optional[UserEntity]: The user entity if found, otherwise None.
        """
        log.info(f"Searching for user by email: {email.value}")
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.email == email.value)
            )
            user_model = result.scalar_one_or_none()

            if user_model:
                log.info(f"User found with email: {email.value}")
                return self._model_to_entity(user_model)
            else:
                log.info(f"No user found with email: {email.value}")
                return None

        except SQLAlchemyError as e:
            log.error(f"Database error while searching for user by email {email.value}: {e}")
            raise Exception("Database error occurred while searching for user")
        except Exception as e:
            log.error(f"Unexpected error while searching for user by email {email.value}: {e}")
            raise

    @retry_read_operation()
    async def find_by_role(self, role: UserRole, limit: Optional[int] = None, offset: Optional[int] = None) -> \
            AsyncIterator[UserEntity]:
        """
        Find users by their role.

        Args:
            role (UserRole): The role to filter by.
            limit (Optional[int]): The maximum number of results to return.
            offset (Optional[int]): The offset for pagination.

        Returns:
            AsyncIterator[UserEntity]: An iterator of user entities matching the role.
        """
        log.info(f"Searching for users by role: {role}, limit: {limit}, offset: {offset}")
        try:
            query = select(UserModel).where(UserModel.role == role)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            result = await self.session.stream_scalars(query)
            user_count = 0

            async for user_model in result:
                resolved_user_model = await user_model
                user_count += 1
                log.debug(f"Retrieved user {user_count} with role {role}: {resolved_user_model.id}")
                yield self._model_to_entity(resolved_user_model)

            log.info(f"Successfully retrieved {user_count} users with role: {role}")

        except SQLAlchemyError as e:
            log.error(f"Database error while searching for users by role {role}: {e}")
            raise Exception("Database error occurred while searching for users by role")
        except Exception as e:
            log.error(f"Unexpected error while searching for users by role {role}: {e}")
            raise

    @retry_read_operation()
    async def find_by_status(self, status: UserStatus, limit: Optional[int] = None, offset: Optional[int] = None) -> \
            AsyncIterator[UserEntity]:
        """
        Find users by their status.

        Args:
            status (UserStatus): The status to filter by.
            limit (Optional[int]): The maximum number of results to return.
            offset (Optional[int]): The offset for pagination.

        Returns:
            AsyncIterator[UserEntity]: An iterator of user entities matching the status.
        """
        log.info(f"Searching for users by status: {status}, limit: {limit}, offset: {offset}")
        try:
            query = select(UserModel).where(UserModel.user_status == status)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            result = await self.session.stream_scalars(query)
            user_count = 0

            async for user_model in result:
                resolved_user_model = await user_model
                user_count += 1
                log.debug(f"Retrieved user {user_count} with status {status}: {resolved_user_model.id}")
                yield self._model_to_entity(resolved_user_model)

            log.info(f"Successfully retrieved {user_count} users with status: {status}")

        except SQLAlchemyError as e:
            log.error(f"Database error while searching for users by status {status}: {e}")
            raise Exception("Database error occurred while searching for users by status")
        except Exception as e:
            log.error(f"Unexpected error while searching for users by status {status}: {e}")
            raise

    @retry_read_operation()
    async def email_exists(self, email: Email, exclude_id: Optional[UserId] = None) -> bool:
        """
        Check if an email address exists in the database.

        Args:
            email (Email): The email address to check.
            exclude_id (Optional[UserId]): An optional user ID to exclude from the check.

        Returns:
            bool: True if the email exists, otherwise False.
        """
        log.info(f"Checking if email exists: {email.value}, excluding ID: {exclude_id.value if exclude_id else 'None'}")
        try:
            query = select(UserModel).where(UserModel.email == email.value)
            if exclude_id:
                query = query.where(UserModel.id != exclude_id.value)

            result = await self.session.execute(query)
            exists = result.scalar_one_or_none() is not None

            log.info(f"Email {email.value} exists: {exists}")
            return exists

        except SQLAlchemyError as e:
            log.error(f"Database error while checking email existence {email.value}: {e}")
            raise Exception("Database error occurred while checking email existence")
        except Exception as e:
            log.error(f"Unexpected error while checking email existence {email.value}: {e}")
            raise

    @retry_write_operation()
    async def save(self, entity: UserEntity) -> UserEntity:
        """
        Save a user entity to the database.

        Args:
            entity (UserEntity): The user entity to save.

        Returns:
            UserEntity: The saved user entity.
        """
        log.info(f"Saving user entity: {entity.email}")

        if entity is None:
            log.error("Attempted to save None entity")
            raise ValueError("The entity to save cannot be None.")

        user_model = self._entity_to_model(entity)

        try:
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)

            log.info(f"User entity saved successfully: {user_model.id}")
            return self._model_to_entity(user_model)

        except SQLAlchemyError as e:
            log.error(f"Failed to save user entity {entity.email.value}: {e}")
            await self.session.rollback()
            raise Exception("Failed to save the user entity to the database.")

    @retry_read_operation()
    async def find_by_id(self, entity_id: UserId) -> Optional[UserEntity]:
        """
        Find a user by their ID.

        Args:
            entity_id (UserId): The ID of the user to find.

        Returns:
            Optional[UserEntity]: The user entity if found, otherwise None.
        """
        log.info(f"Searching for user by ID: {entity_id.value}")
        try:
            user_model: Optional[UserModel] = await self.session.get(UserModel, entity_id.value)

            if user_model:
                log.info(f"User found with ID: {entity_id.value}")
                return self._model_to_entity(user_model)
            else:
                log.info(f"No user found with ID: {entity_id.value}")
                return None

        except SQLAlchemyError as e:
            log.error(f"Database error while searching for user by ID {entity_id.value}: {e}")
            raise Exception("Database error occurred while searching for user")
        except Exception as e:
            log.error(f"Unexpected error while searching for user by ID {entity_id.value}: {e}")
            raise

    @retry_read_operation()
    async def find_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[UserEntity]:
        """
        Find all users in the database with optional pagination.
        """
        try:
            # Input validation
            if limit is not None and limit <= 0:
                raise ValueError("Limit must be greater than 0")
            if offset is not None and offset < 0:
                raise ValueError("Offset must be greater than or equal to 0")

            # Use the session context manager properly
            async with self.session as session:
                query = select(UserModel)
                log.info(f"Executing query to find all users with limit: {limit}, offset: {offset}")

                if limit:
                    query = query.limit(limit)
                if offset:
                    query = query.offset(offset)

                result = await session.execute(query)
                users_models = result.scalars().all()

                log.info(f"Successfully retrieved {len(users_models)} users from database")

                # Convert models to entities
                user_entities = []
                for user_model in users_models:
                    try:
                        user_entity = self._model_to_entity(user_model)
                        user_entities.append(user_entity)
                    except Exception as e:
                        log.error(f"Error converting user model to entity for user ID {user_model.id}: {e}")
                        continue

                return user_entities

        except ValueError as e:
            log.error(f"Invalid parameters provided: {e}")
            raise e

        except TimeoutError as e:
            log.error(f"Database connection timeout while fetching users: {e}")
            raise Exception("Database connection timeout. Please try again later.")

        except OperationalError as e:
            log.error(f"Database operational error while fetching users: {e}")
            raise Exception("Database operational error. Please try again later.")

        except SQLAlchemyError as e:
            log.error(f"SQLAlchemy error while fetching users: {e}")
            raise Exception("Database error occurred while fetching users.")

        except Exception as e:
            log.error(f"Unexpected error while fetching all users: {e}", exc_info=True)
            raise Exception("An unexpected error occurred while fetching users.")

    @retry_read_operation()
    async def exists(self, entity_id: UserId) -> bool:
        """
        Check if a user exists in the database.

        Args:
            entity_id (UserId): The ID of the user to check.

        Returns:
            bool: True if the user exists, otherwise False.
        """
        log.info(f"Checking if user exists with ID: {entity_id.value}")

        user_model = await self.find_by_id(entity_id)
        exists = user_model is not None

        log.info(f"User with ID {entity_id.value} exists: {exists}")

        return exists

    @retry_write_operation()
    async def update(self, entity: UserEntity) -> Optional[UserEntity]:
        """
        Update a user entity in the database.

        Args:
            entity (UserEntity): The user entity to update.

        Returns:
            Optional[UserEntity]: The updated user entity if successful, otherwise None.
        """
        log.info(f"Updating user entity: {entity.id}")
        try:
            user_model: Optional[UserModel] = await self.session.get(UserModel, entity.id.value)
            if not user_model:
                log.warning(f"User not found for update: {entity.id}")
                return None

            # Update fields directly on the existing model
            user_model.update_user_model_data(
                first_name=entity.first_name,
                last_name=entity.last_name,
            )

            # Since we modified the existing model, it's already tracked by the session
            # We don't need to add it again, just commit the changes
            await self.session.commit()

            log.info(f"User entity updated successfully: {entity.id}")

            return self._model_to_entity(user_model)

        except SQLAlchemyError as e:
            log.error(f"Database error while updating user {entity.id}: {e}")
            await self.session.rollback()
            raise Exception("Database error occurred while updating user")
        except Exception as e:
            log.error(f"Unexpected error while updating user {entity.id}: {e}")
            await self.session.rollback()
            raise

    @retry_critical_operation()
    async def delete(self, entity_id: UserId) -> bool:
        """
        Delete a user by their ID.

        Args:
            entity_id (UserId): The ID of the user to delete.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        log.info(f"Deleting user with ID: {entity_id.value}")
        try:
            user_model: Optional[UserModel] = await self.session.get(UserModel, entity_id.value)
            if not user_model:
                log.warning(f"User not found for deletion: {entity_id.value}")
                return False

            await self.session.delete(user_model)
            await self.session.commit()

            log.info(f"User deleted successfully: {entity_id.value}")
            return True

        except SQLAlchemyError as e:
            log.error(f"Database error while deleting user {entity_id.value}: {e}")
            await self.session.rollback()
            raise Exception("Database error occurred while deleting user")
        except Exception as e:
            log.error(f"Unexpected error while deleting user {entity_id.value}: {e}")
            await self.session.rollback()
            raise

    @staticmethod
    def _model_to_entity(model: UserModel) -> UserEntity:
        log.debug(f"Converting UserModel to UserEntity for ID: {model.id}")
        try:
            # Create UserEntity directly using the create factory method
            return UserEntity.create(
                user_id=UserId.from_string(str(model.id)),  # Convert UUID to UserId
                first_name=model.first_name,
                last_name=model.last_name,
                email=Email(str(model.email)),  # Convert string to Email value object
                role=model.role,
                user_status=model.user_status,
                password_hash=model.password_hash,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        except Exception as e:
            log.error(f"Error converting UserModel to UserEntity for ID {model.id}: {e}")
            raise

    @staticmethod
    def _entity_to_model(entity: UserEntity) -> UserModel:
        log.debug(f"Converting UserEntity to UserModel for ID: {entity.id}")
        try:
            # Create UserModel directly with proper value extraction
            user_model = UserModel(
                id=entity.id.value,  # Extract UUID from UserId
                first_name=entity.first_name,
                last_name=entity.last_name,
                email=entity.email.value,  # Extract string from Email
                role=entity.role,
                user_status=entity.user_status,
                password_hash=entity.password_hash,
                created_at=entity.created_at,
                updated_at=entity.updated_at
            )

            return user_model
        except Exception as e:
            log.error(f"Error converting UserEntity to UserModel for ID {entity.id}: {e}")
            raise
