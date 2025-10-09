from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId

T = TypeVar('T')
ID = TypeVar('ID')


class BaseRepository(Generic[T, ID], ABC):
    """
    Abstract base class for repositories managing entities.

    This interface defines the contract for repository implementations, ensuring
    consistent behavior for CRUD operations across different entity types.
    """

    @abstractmethod
    async def save(self, entity: BaseEntity) -> BaseEntity:
        """
        Save a new entity in the repository.

        Args:
            entity (BaseEntity): The entity instance to save.

        Returns:
            BaseEntity: The saved entity instance.
        """
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: EntityId) -> Optional[BaseEntity]:
        """
        Retrieve an entity by its unique identifier.

        Args:
            entity_id (EntityId): The unique identifier of the entity.

        Returns:
            Optional[BaseEntity]: The entity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def find_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[BaseEntity]:
        """
        Retrieve all entities, with optional pagination.

        Args:
            limit (Optional[int]): Maximum number of entities to return.
            offset (Optional[int]): Number of entities to skip before starting to collect the result set.

        Returns:
            List[BaseEntity]: A list of entities.
        """
        pass

    @abstractmethod
    async def exists(self, entity_id: EntityId) -> bool:
        """
        Check if an entity exists by its unique identifier.

        Args:
            entity_id (EntityId): The unique identifier of the entity.

        Returns:
            bool: True if the entity exists, False otherwise.
        """
        pass

    @abstractmethod
    async def update(self, entity: BaseEntity) -> Optional[BaseEntity]:
        """
        Update an existing entity in the repository.

        Args:
            entity (BaseEntity): The entity instance to update.

        Returns:
            Optional[BaseEntity]: The updated entity if successful, otherwise None.
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        """
        Remove an entity by its unique identifier.

        Args:
            entity_id (EntityId): The unique identifier of the entity to delete.

        Returns:
            bool: True if the entity was deleted, False if not found.
        """
        pass
