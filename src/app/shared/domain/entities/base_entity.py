from datetime import UTC, datetime

from src.app.shared.domain.value_objects.entity_id import EntityId


class BaseEntity:
    def __init__(
        self,
        id: EntityId,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self._id = id
        self._created_at = (
            created_at if created_at is not None else datetime.now(tz=UTC)
        )
        self._updated_at = (
            updated_at if updated_at is not None else datetime.now(tz=UTC)
        )

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def mark_as_updated(self) -> None:
        self._updated_at = datetime.now(tz=UTC)
