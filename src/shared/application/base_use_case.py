from dataclasses import dataclass


@dataclass
class BaseUseCase:
    MAX_LIMIT = 100  # Set a maximum threshold for the limit

    def validate_pagination(self, limit: int, offset: int):
        if limit < 0 or limit > self.MAX_LIMIT:
            raise ValueError(f"Limit must be between 0 and {self.MAX_LIMIT}")
        if offset < 0:
            raise ValueError("Offset must be a non-negative integer")
