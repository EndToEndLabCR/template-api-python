"""
Shared test fixtures and configuration.

IMPORTANT: Environment variables are set at module level BEFORE any app imports.
This ensures AppConfig loads config_test.yml, not config_local.yml.
"""
import os
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Environment setup — runs before any test module import
# ---------------------------------------------------------------------------
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("POSTGRES_PASSWORD", "test-password")

# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def pytest_configure(config):
    """Register custom markers (also defined in pytest.ini for reference)."""
    config.addinivalue_line("markers", "unit: Fast tests with no external dependencies")
    config.addinivalue_line("markers", "integration: Tests requiring database or external services")
    config.addinivalue_line("markers", "e2e: Full system tests")


# ---------------------------------------------------------------------------
# Shared mocks
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_user_repository():
    """
    Fully mocked UserRepository. Shared across user feature tests.
    All methods return AsyncMock by default — set .return_value or .side_effect in tests.
    """
    mock = AsyncMock(spec=[
        "save", "find_by_id", "find_all", "exists", "update", "delete",
        "find_by_email", "find_by_name", "find_by_reset_token_hash",
    ])
    # Default async methods return None (safe default)
    mock.save.return_value = None
    mock.find_by_id.return_value = None
    mock.find_by_email.return_value = None
    mock.find_by_name.return_value = None
    mock.find_by_reset_token_hash.return_value = None
    mock.exists.return_value = False
    return mock


# ---------------------------------------------------------------------------
# FastAPI TestClient with overridden dependencies
# ---------------------------------------------------------------------------
@pytest.fixture
def client(mock_user_repository):
    """
    FastAPI TestClient with DB-dependent dependencies overridden.
    Creates a default authenticated user for routes that require auth.
    """
    # Import app modules inside fixture to guarantee env vars are already set
    from src.app.app import fastApiApp
    from src.app.features.presentation.web import dependencies as deps
    from src.app.features.presentation.web.auth_dependencies import get_current_user
    from src.app.features.application.services.user_service import UserService
    from src.app.features.application.services.password_service import PasswordService
    from src.app.features.domain.entities.user_entity import UserEntity
    from src.app.features.domain.value_objects.email import Email
    from src.shared.domain.value_objects.entity_id import EntityId

    # Build real services with the mock repo
    user_svc = UserService(mock_user_repository)
    password_svc = PasswordService(mock_user_repository)

    # Create a default authenticated user for routes needing auth
    current_user = UserEntity(
        id=EntityId.generate(),
        email=Email("test@example.com"),
        first_name="Test",
        last_name="User",
        password_hash="$2b$12$LJ3m4ys3LkDummyHashForTestingPurposes",
    )

    # Override DB-dependent dependencies
    fastApiApp.dependency_overrides[deps.get_user_service] = lambda: user_svc
    fastApiApp.dependency_overrides[deps.get_password_service] = lambda: password_svc

    # Override auth dependency (bypass JWT validation + DB lookup)
    fastApiApp.dependency_overrides[get_current_user] = lambda: current_user

    with TestClient(fastApiApp) as c:
        yield c

    # Clean up overrides after test
    fastApiApp.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Utility: reset AppConfig singleton between tests (if needed)
# ---------------------------------------------------------------------------
@pytest.fixture
def reset_app_config():
    """
    Use this fixture in tests that change APP_ENV or need a fresh config load.

    Usage:
        def test_something(reset_app_config):
            ...
    """
    from src.app.config.app_config import AppConfig
    AppConfig.reset_instance()
    yield
    AppConfig.reset_instance()
