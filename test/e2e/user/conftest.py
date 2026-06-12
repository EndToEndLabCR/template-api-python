"""E2E fixtures for user feature."""

import pytest


@pytest.fixture
def sample_user_entity():
    """A realistic UserEntity for E2E test assertions."""
    from src.app.features.domain.entities.user_entity import UserEntity
    from src.app.features.domain.value_objects.email import Email
    from src.shared.domain.value_objects.entity_id import EntityId

    return UserEntity(
        id=EntityId.generate(),
        email=Email("test@example.com"),
        first_name="Test",
        last_name="User",
        password_hash="$2b$12$LJ3m4ys3LkDummyHashForTestingPurposes",
    )
