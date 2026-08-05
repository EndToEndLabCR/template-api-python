"""User feature test fixtures."""
import pytest


@pytest.fixture
def user_service(mock_user_repository):
    """UserService wired with a mock repository."""
    from src.app.features.application.services.user_service import UserService
    return UserService(mock_user_repository)


@pytest.fixture
def password_service(mock_user_repository):
    """PasswordService wired with a mock repository."""
    from src.app.features.application.services.password_service import PasswordService
    return PasswordService(mock_user_repository)


@pytest.fixture
def sample_user_entity():
    """A realistic UserEntity with valid data for test assertions."""
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
