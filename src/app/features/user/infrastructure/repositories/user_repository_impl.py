from datetime import datetime
from typing import Optional

from sqlalchemy import select, update as sql_update
import sqlalchemy.exc

from src.app.features.user.domain.entities.user_entity import UserEntity
from src.app.features.user.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError,
)
from src.app.features.user.domain.repositories.user_repository import UserRepository
from src.app.features.user.infrastructure.models.user_model import UserModel
from src.app.features.user.infrastructure.mappers.user_model_mapper import (
    UserModelMapper,
)
from src.app.shared.domain.value_objects.email import Email
from src.app.shared.domain.value_objects.entity_id import EntityId

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.shared.utils.log_util import log


class DatabaseConnectionError(Exception):
    """Custom exception to indicate database connection errors."""
    pass


class UserRepositoryImpl(UserRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def find_by_id(self, entity_id: EntityId) -> Optional[UserEntity]:
        try:
            log.info(f"start get user by id: {entity_id.value}")
            user_model: Optional[UserModel] = await self.db_session.get(
                UserModel, entity_id.value
            )
            if user_model is None:
                log.info(f"user by id {entity_id.value} not found")
                return None
            log.info(f"completed get user by id {entity_id.value}")
            return UserModelMapper.to_entity(user_model)
        except sqlalchemy.exc.OperationalError as db_error:
            log.error(
                f"Database connection error while finding user by id: {entity_id.value}. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error
        except Exception as e:
            log.error(f"Error finding user by id: {entity_id.value} Exceptions: {str(e)}")
            raise

    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        result = await self.db_session.execute(
            select(UserModel).where(UserModel.email == email.value)
        )
        user_model = result.scalar_one_or_none()
        if user_model is None:
            log.info(f"User with email {email.value} not found.")
            return None
        log.info(f"User with email {email.value} found.")
        return UserModelMapper.to_entity(user_model)

    async def find_by_reset_token_hash(self, token_hash: str) -> Optional[UserEntity]:
        try:
            result = await self.db_session.execute(
                select(UserModel).where(
                    UserModel.password_reset_token_hash == token_hash
                )
            )
            user_model = result.scalar_one_or_none()
            if user_model is None:
                log.info("User with given reset token hash not found.")
                return None
            log.info("User found by reset token hash.")
            return UserModelMapper.to_entity(user_model)
        except sqlalchemy.exc.OperationalError as db_error:
            log.error(
                f"Database connection error while finding user by reset token. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error
        except Exception as e:
            log.error(f"Error finding user by reset token: {str(e)}")
            raise

    async def save(self, user: UserEntity) -> UserEntity:
        try:
            result = await self.db_session.execute(
                select(UserModel).where(UserModel.email == user.email.value)
            )
            if result.scalar_one_or_none():
                log.warning(f"[save] User with email {user.email} already exists")
                raise UserAlreadyExistsError(user.email.value)

            user_model = UserModelMapper.to_model(user)
            self.db_session.add(user_model)
            await self.db_session.commit()
            await self.db_session.refresh(user_model)

            log.info(f"[save] User persisted successfully. id={user_model.id}")
            return UserModelMapper.to_entity(user_model)

        except sqlalchemy.exc.IntegrityError as e:
            await self.db_session.rollback()
            log.error(f"[save] IntegrityError while saving user with email {user.email}: {e}")
            raise UserAlreadyExistsError(user.email.value) from e

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[save] Unexpected error while saving user with email {user.email}: {e}")
            raise

    async def update(self, entity: UserEntity) -> Optional[UserEntity]:
        try:
            user_model = await self.db_session.get(UserModel, entity.id.value)

            if user_model is None:
                log.warning(f"User with id {entity.id.value} not found for update.")
                return None

            user_model.email = entity.email.value
            user_model.display_name = entity.display_name
            user_model.role = entity.role.value
            user_model.password_hash = entity.password_hash

            await self.db_session.commit()
            await self.db_session.refresh(user_model)

            log.info(f"User with id {entity.id.value} updated successfully.")
            return UserModelMapper.to_entity(user_model)

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(
                f"Database connection error while updating user {entity.id.value}. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"Error updating user {entity.id.value}: {str(e)}")
            raise

    async def delete(self, entity_id: EntityId) -> bool:
        try:
            existing_user = await self.db_session.get(UserModel, entity_id.value)
            if not existing_user:
                log.info(f"User with id {entity_id.value} not found for deletion.")
                return False
            await self.db_session.delete(existing_user)
            await self.db_session.commit()
            log.info(f"User with id {entity_id.value} successfully deleted.")
            return True
        except sqlalchemy.exc.OperationalError as db_error:
            log.error(
                f"Database connection error while deleting user: {entity_id.value}. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error
        except Exception as e:
            log.error(f"Error deleting user: {entity_id.value} Exceptions: {str(e)}")
            raise

    async def set_password_reset_token(
        self, email: Email, token_hash: str, expires_at: datetime
    ) -> bool:
        try:
            result = await self.db_session.execute(
                sql_update(UserModel)
                .where(UserModel.email == email.value)
                .values(
                    password_reset_token_hash=token_hash,
                    password_reset_expires_at=expires_at,
                )
            )
            await self.db_session.commit()
            updated = result.rowcount > 0
            if updated:
                log.info(f"Password reset token set for email: {email.value}")
            else:
                log.warning(f"Password reset token not set — email not found: {email.value}")
            return updated
        except sqlalchemy.exc.OperationalError as db_error:
            log.error(f"DB error setting password reset token: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error
        except Exception as e:
            await self.db_session.rollback()
            log.error(f"Error setting password reset token: {str(e)}")
            raise

    async def reset_password(
        self, token_hash: str, new_password_hash: str
    ) -> bool:
        """Atomically reset password if token exists and is not expired."""
        try:
            result = await self.db_session.execute(
                sql_update(UserModel)
                .where(
                    UserModel.password_reset_token_hash == token_hash,
                    UserModel.password_reset_expires_at > datetime.now(),
                )
                .values(
                    password_hash=new_password_hash,
                    password_reset_token_hash=None,
                    password_reset_expires_at=None,
                )
            )
            await self.db_session.commit()
            updated = result.rowcount > 0
            if updated:
                log.info("Password reset successfully via token hash.")
            else:
                log.warning("Password reset failed — token hash not found.")
            return updated
        except sqlalchemy.exc.OperationalError as db_error:
            log.error(f"DB error resetting password: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error
        except Exception as e:
            await self.db_session.rollback()
            log.error(f"Error resetting password: {str(e)}")
            raise
