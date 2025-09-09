from uuid import UUID, uuid4
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError("UserId must be a valid UUID")

    @classmethod
    def generate(cls) -> "UserId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, user_id: str) -> "UserId":
        try:
            return cls(UUID(user_id))
        except ValueError:
            raise ValueError(f"Invalid UUID format: {user_id}")

    def __str__(self) -> str:
        return str(self.value)
