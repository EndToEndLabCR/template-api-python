from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')
ID = TypeVar('ID')


class BaseRepository(Generic[T, ID], ABC):
    """Base repository interface"""

    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        pass

    @abstractmethod
    async def find_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        pass

    @abstractmethod
    async def exists(self, entity_id: ID) -> bool:
        pass

    @abstractmethod
    async def update(self, entity: T) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        pass
