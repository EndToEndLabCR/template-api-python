# Unify User & Auth Features

## Goal

Make user and auth features fully functional using `shared/`, `config/`, and `composition/` modules.
The `auth/` feature becomes the canonical auth system (login, register, refresh).
The `user/` feature handles CRUD and password reset.
All imports standardized to `src.app.*`.
All dependency injection centralized through `composition/__init__.py`.

## Constraints

- Clean architecture boundaries preserved (Domain → Application → Infrastructure → Presentation)
- DB can be recreated from scratch; no backward-compatibility concern
- Do not change shared infrastructure modules (logging, JWTHandler, PasswordHandler, lockout, rate limiter, engine factory, health checks, exception handlers) — they are already complete
- Keep `passlib` in requirements (remove later if still unused)

---

## Pre-Flight Checklist

Before starting Phase 1, verify these prerequisites to avoid startup crashes:

| # | Check | Action |
|---|-------|--------|
| 1 | `slowapi` installed | Add `slowapi` to `requirements.txt` and `pip install slowapi` |
| 2 | `SECRET_KEY` ≥ 32 chars | Update `.env` line 3: `SECRET_KEY=change-me-to-a-secure-secret-at-least-32-characters-long` |
| 3 | `.env` no leading space | Fix `.env` line 1: ` APP_ENV=local` → `APP_ENV=local` |
| 4 | `python-json-logger` installed | `pip install python-json-logger` (used by logging formatters) |
| 5 | All deps fresh | `pip install -r requirements.txt` |

---

## Phase 1 — Persistence Foundation

### 1.1 Fix `shared/persistence/__init__.py`

**Problem:** Imports `Base` and `BaseModel` from non-existent `base_model.py`.

**Fix:** Declare them inline. Replace entire file:

```python
"""Persistence layer: database engine, session, and base model."""

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class BaseModel(Base):
    """Abstract base for all SQLAlchemy models. Uses UUID v4 string PK."""
    __abstract__ = True
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

from src.app.shared.persistence.engine_factory import close_engine, get_engine  # noqa: E402

__all__ = ["Base", "BaseModel", "close_engine", "get_engine"]
```

**Files changed:**
- `src/app/shared/persistence/__init__.py`

### 1.2 Fix `alembic/env.py`

**Two problems:**
1. `Base` import from non-existent path `src.shared.infrastructure.models.base_model`
2. Config key `"postgres"` is wrong — config uses `"persistence.postgres"`

**Replace lines 16-17 (the import) and lines 29-36 (the config block):**

```python
# Line 16-17: replace broken Base import
from src.app.shared.persistence import Base

# Lines 29-36: replace config key from "postgres" to "persistence.postgres"
postgres_config: dict = AppConfig.instance().get_config("persistence.postgres", {})
```

**Files changed:**
- `alembic/env.py`

### 1.3 Fix `UserModel` — add `BaseModel` import, `role` column

```python
from sqlalchemy import Column, String, DateTime
from src.app.shared.persistence import BaseModel

class UserModel(BaseModel):
    __tablename__ = 'users'
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    password_hash = Column(String(255), nullable=False)
    password_reset_token_hash = Column(String(255), nullable=True)
    password_reset_expires_at = Column(DateTime, nullable=True)
```

**Files changed:**
- `src/app/features/user/infrastructure/models/user_model.py`

### 1.4 Fix `UserRepositoryImpl.save()` and `update()` — persist `role`

**`save()`** — add `role` to the `UserModel()` constructor (around line 105-111):

```python
user_model = UserModel(
    id=user.id.value,
    email=user.email.value,
    first_name=user.first_name,
    last_name=user.last_name,
    role=user.role.value,                         # ← ADD THIS
    password_hash=user.password_hash,
    password_reset_token_hash=user.password_reset_token_hash,   # ← ADD THIS
    password_reset_expires_at=user.password_reset_expires_at,   # ← ADD THIS
)
```

**`update()`** — add `role` to the attribute assignments (around line 145):

```python
user_model.role = entity.role.value               # ← ADD THIS
```

**Files changed:**
- `src/app/features/user/infrastructure/repository/user_repository_impl.py`

### 1.5 Recreate migrations

Delete all existing version files and generate a fresh migration.

```bash
rm alembic/versions/*.py
alembic revision --autogenerate -m "initial_user_model_with_role"
```

**Files changed:**
- `alembic/versions/` — all old files deleted, one new migration created

---

## Phase 2 — Domain Entity Fixes

### 2.1 Fix `UserEntity` — imports, role, display_name

Replace entire file. Adds `role` attribute (defaults to VIEWER), `display_name` property, fixes imports:

```python
from datetime import datetime
from typing import Optional

from src.app.features.user.domain.value_objects.user_role import UserRole
from src.app.shared.domain.entities.base_entity import BaseEntity
from src.app.shared.domain.value_objects.email import Email
from src.app.shared.domain.value_objects.entity_id import EntityId


class UserEntity(BaseEntity):

    def __init__(self, id: EntityId, email: Email, first_name: str, last_name: str, password_hash: str,
                 password_reset_token_hash: Optional[str] = None,
                 password_reset_expires_at: Optional[datetime] = None,
                 role: UserRole = UserRole.VIEWER,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.password_hash = password_hash
        self.password_reset_token_hash = password_reset_token_hash
        self.password_reset_expires_at = password_reset_expires_at
        super().__init__(id, created_at, updated_at)

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**Files changed:**
- `src/app/features/user/domain/entities/user_entity.py`

### 2.2 Populate domain exceptions

The file `src/app/features/user/domain/exceptions/user_exceptions.py` is currently empty but imported by `exception_handlers.py` (which expects `UserAlreadyExistsError` and `UserNotFoundError`). Fill it:

```python
"""Domain-level exceptions for the user feature."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""

    def __init__(self, email: str):
        self.email = email
        self.message = f"User with email {email} already exists."
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Raised when a user is not found by ID or email."""

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.message = f"User not found: {identifier}"
        super().__init__(self.message)
```

**Note:** The application-layer exceptions (`UserDoesNotExistException`, `UserAlreadyExistsException`, `UserEmailNotFoundException`) remain in `application/exceptions/` unchanged. The domain-layer exceptions added here are what `exception_handlers.py` expects.

**Files changed:**
- `src/app/features/user/domain/exceptions/user_exceptions.py`

### 2.3 Fix `user_model_mapper.py` — map `role`, fix `Email` import

Replace entire file:

```python
from src.app.features.user.domain.entities.user_entity import UserEntity
from src.app.features.user.domain.value_objects.user_role import UserRole
from src.app.features.user.infrastructure.models.user_model import UserModel
from src.app.shared.domain.value_objects.email import Email
from src.app.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(user_model: UserModel) -> UserEntity:
    return UserEntity(
        id=EntityId(user_model.id),
        email=Email(user_model.email),
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        role=UserRole(user_model.role),
        password_hash=user_model.password_hash,
        password_reset_token_hash=user_model.password_reset_token_hash,
        password_reset_expires_at=user_model.password_reset_expires_at,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )
```

**Files changed:**
- `src/app/features/user/infrastructure/repository/user_model_mapper.py`

---

## Phase 3 — Standardize Imports (user/ feature)

Convert all `app.*` imports to `src.app.*` and fix all broken `Email` import paths (currently pointing to non-existent `app.features.user.domain.value_objects.email` → should be `src.app.shared.domain.value_objects.email`).

### Files to fix (import changes only, no logic changes)

| File | Fix |
|------|-----|
| `features/user/domain/repositories/user_repository.py` | `app.features.*` → `src.app.features.*`, `app.shared.*` → `src.app.shared.*` |
| `features/user/application/mappers/user_dto_mapper.py` | Fix `Email` import path, `app.*` → `src.app.*` |
| `features/user/application/services/user_service.py` | Fix `Email` import path, `app.*` → `src.app.*` |
| `features/user/application/services/password_service.py` | `app.*` → `src.app.*` |
| `features/user/application/use_cases/create_user.py` | `app.*` → `src.app.*` |
| `features/user/application/use_cases/get_user_by_id.py` | `app.*` → `src.app.*` |
| `features/user/application/use_cases/delete_user_by_id.py` | `app.*` → `src.app.*` |
| `features/user/application/use_cases/forgot_password.py` | Fix `Email` import path, `app.*` → `src.app.*` |
| `features/user/application/use_cases/reset_password.py` | `app.*` → `src.app.*` |
| `features/user/infrastructure/repository/user_repository_impl.py` | Fix `UserAlreadyExistsException` import path, fix `Email` import path, `app.*` → `src.app.*`, remove broken `src.shared.domain.repositories.base_repository` import (unused) |
| `features/user/presentation/web/routes/user_routes.py` | `app.*` → `src.app.*`. **Also remove `POST /register` endpoint** (lines 59-79) — registration is now in the auth feature at `/api/v1/register` |
| `features/user/presentation/web/routes/password_routes.py` | `app.*` → `src.app.*` |

### Note on `dependencies.py`

`src/app/features/user/presentation/web/dependencies.py` is a special case — it creates a new `PostgresDbConnection` engine per request and imports from broken paths. We rewrite it in **Phase 5** to use the `composition/` root and `get_engine()` singleton.

### `user_repository_impl.py` specific fixes

1. **Line 6**: `from app.features.user.application import UserAlreadyExistsException`
   → `from src.app.features.user.domain.exceptions.user_exceptions import UserAlreadyExistsError`
2. **Line 9**: `from app.features.user.domain.value_objects.email import Email`
   → `from src.app.shared.domain.value_objects.email import Email`
3. **Line 12**: `from src.shared.domain.repositories.base_repository import ID, T`
   → **Delete this line** (file doesn't exist, and `ID`/`T` are only used in stub method signatures — replace with `Any`)

---

## Phase 4 — Implement Composition Root

Replace the empty `src/app/composition/__init__.py` with the full dependency injection factories.

```python
"""
Composition root — wires all dependencies for FastAPI dependency injection.
Centralizes creation of singletons, repositories, use cases, and services.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config.app_config import AppConfig
from src.app.features.auth.application.use_cases.login_user import LoginUserUseCase
from src.app.features.auth.application.use_cases.register_user import RegisterUserUseCase
from src.app.features.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from src.app.features.user.application.services.password_service import PasswordService
from src.app.features.user.application.services.user_service import UserService
from src.app.features.user.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.app.shared.infrastructure.security.jwt_handler import JWTHandler
from src.app.shared.persistence.engine_factory import get_engine

_config = AppConfig.instance()


# --- Singletons ---

@lru_cache(maxsize=1)
def get_jwt_handler() -> JWTHandler:
   """Singleton JWTHandler wired from config. Cached via lru_cache."""
   return JWTHandler(
      secret_key=_config.get_config("security.jwt.secret_key", ""),
      algorithm=_config.get_config("security.jwt.algorithm", "HS256"),
      expiration_minutes=int(_config.get_config("security.jwt.access_token_expire_minutes", 1440)),
      refresh_expiration_minutes=10080,  # 7 days
   )


# --- Database session ---

async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
   """Yield a database session from the singleton engine."""
   engine = get_engine()
   async with engine.get_session() as session:
      yield session


# --- User repositories ---

async def get_user_repository(
        session: AsyncSession = Depends(get_database_session),
) -> UserRepositoryImpl:
   return UserRepositoryImpl(session)


# --- Auth use cases ---

async def get_login_use_case(
        repo: UserRepositoryImpl = Depends(get_user_repository),
) -> LoginUserUseCase:
   return LoginUserUseCase(repo, get_jwt_handler())


async def get_register_use_case(
        repo: UserRepositoryImpl = Depends(get_user_repository),
) -> RegisterUserUseCase:
   return RegisterUserUseCase(repo, get_jwt_handler())


async def get_refresh_token_use_case(
        repo: UserRepositoryImpl = Depends(get_user_repository),
) -> RefreshTokenUseCase:
   return RefreshTokenUseCase(repo, get_jwt_handler())


# --- User services ---

async def get_user_service(
        repo: UserRepositoryImpl = Depends(get_user_repository),
) -> UserService:
   return UserService(repo)


async def get_password_service(
        repo: UserRepositoryImpl = Depends(get_user_repository),
) -> PasswordService:
   return PasswordService(repo)
```

**Key design decision:** `get_jwt_handler()` uses `@lru_cache(maxsize=1)` for a clean singleton. Both the use case factories and `get_current_user` (in `auth_dependencies.py`) call it directly via `Depends(get_jwt_handler)` — all consumers get the same cached instance.

**Files changed:**
- `src/app/composition/__init__.py`

### 4.1 Fix `auth_dependencies.py` import

**`src/app/shared/presentation/auth_dependencies.py`** line 16:
```python
# Before:
from src.app.composition.infrastructure import get_jwt_handler

# After:
from src.app.composition import get_jwt_handler
```

The rest of the file stays unchanged. `get_current_user` and `require_admin` function correctly with `Depends(get_jwt_handler)` now pointing to the composition root singleton.

**Files changed:**
- `src/app/shared/presentation/auth_dependencies.py`

---

## Phase 5 — Fix `dependencies.py` (user feature)

Rewrite `src/app/features/user/presentation/web/dependencies.py` to forward to composition root.

```python
"""
User feature dependencies — delegates to composition root.
"""
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.composition import (
    get_database_session,
    get_password_service as _get_password_service,
    get_user_service as _get_user_service,
)
from src.app.features.user.application.services.password_service import PasswordService
from src.app.features.user.application.services.user_service import UserService


async def get_user_service(session: AsyncSession = Depends(get_database_session)) -> UserService:
    return await _get_user_service(session=session)

async def get_password_service(session: AsyncSession = Depends(get_database_session)) -> PasswordService:
    return await _get_password_service(session=session)
```

**Files changed:**
- `src/app/features/user/presentation/web/dependencies.py`

---

## Phase 6 — Wire `app.py` Correctly

Rewrite `src/app/app.py` to register the auth feature routes, shared middleware, exception handlers, and health endpoints.

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.config.app_config import AppConfig
from src.app.shared.logging.logger import setup_logging
from src.app.shared.logging.config import load_logging_config
from src.app.shared.presentation.exception_handlers import register_exception_handlers
from src.app.shared.presentation.health_checks import register_health_endpoints

# ── Feature routers ──────────────────────────────────────────────
# Auth feature (login, register, refresh)
from src.app.features.auth.presentation.auth_routes import router as auth_router

# User feature (CRUD — GET/DELETE by ID only; registration moved to auth)
from app.features.user.presentation.user_routes import router as user_router

# Password feature (forgot/reset)
from src.app.features.user.presentation.web.routes.password_routes import router as password_router

# ── Config ────────────────────────────────────────────────────────
config = AppConfig.instance()
app_name = config.get_config("app.name", "API")
app_version = config.get_config("app.version", "1.0.0")
ENV = os.getenv("APP_ENV", "local")

# Setup logging
setup_logging(load_logging_config())

# ── App ───────────────────────────────────────────────────────────
fastapi_app = FastAPI(title=app_name, version=app_version)

# Disable docs in non-local/non-test envs
if ENV not in ("local", "test"):
    fastapi_app.docs_url = None
    fastapi_app.redoc_url = None
    fastapi_app.openapi_url = None

# ── CORS ──────────────────────────────────────────────────────────
cors_origins = config.get_config("security.cors_origins", ["http://localhost:5173", "http://localhost:*"])
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared middleware & handlers ──────────────────────────────────
# TODO (follow-up): add SlowAPIMiddleware for rate limiting enforcement
# TODO (follow-up): add CorrelationIdMiddleware for request tracing
# TODO (follow-up): add RequestLoggingMiddleware

# Register exception handlers (404, 409, 422, 429, 500, etc.)
register_exception_handlers(fastapi_app)

# ── Routes ────────────────────────────────────────────────────────
fastapi_app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
fastapi_app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
fastapi_app.include_router(password_router, prefix="/api/v1", tags=["Password"])

# ── Health ────────────────────────────────────────────────────────
register_health_endpoints(fastapi_app)


@fastapi_app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}
```

**Files changed:**
- `src/app/app.py`

---

## Phase 7 — Cleanup

### 7.1 Delete legacy files

```bash
rm src/app/features/user/presentation/web/routes/auth_routes.py
rm src/app/shared/utils/jwt_util.py
rm src/app/shared/presentation/router_registry.py
```

### 7.2 Fix `.env`

Two fixes:
1. **Line 1** — remove leading space: ` APP_ENV=local` → `APP_ENV=local`
2. **Line 3** — ensure >= 32 chars: `SECRET_KEY=secret-ket-123` → `SECRET_KEY=change-me-to-a-secure-secret-at-least-32-characters-long`

### 7.3 Add `slowapi` to `requirements.txt`

Add this line (order doesn't matter):
```
slowapi==0.1.9
```

**Files changed:**
- `.env`
- `requirements.txt`
- `src/app/features/user/presentation/web/routes/auth_routes.py` (deleted)
- `src/app/shared/utils/jwt_util.py` (deleted)
- `src/app/shared/presentation/router_registry.py` (deleted)

---

## Phase 8 — Verification

### 8.1 Install dependencies

```bash
pip install -r requirements.txt
```

### 8.2 Verify imports

```bash
python -c "from src.app.shared.persistence import Base, BaseModel; print('persistence OK')"
python -c "from src.app.features.user.domain.entities.user_entity import UserEntity; print('UserEntity OK')"
python -c "from src.app.features.user.domain.exceptions.user_exceptions import UserAlreadyExistsError, UserNotFoundError; print('exceptions OK')"
python -c "from src.app.composition import get_login_use_case, get_register_use_case, get_refresh_token_use_case, get_jwt_handler; print('composition OK')"
python -c "from src.main import app; print('app OK')"
```

### 8.3 Run DB migration

```bash
alembic upgrade head
```

### 8.4 Start the app

```bash
uvicorn src.main:app --reload
```

### 8.5 Smoke-test endpoints

```bash
# Health
curl -s http://localhost:8000/ | jq
curl -s http://localhost:8000/health
curl -s http://localhost:8000/health/live
curl -s http://localhost:8000/health/ready

# Register
curl -s -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass1!", "firstName": "Test", "lastName": "User"}' | jq

# Login
curl -s -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass1!"}' | jq

# Get user (with token from login/register response)
curl -s http://localhost:8000/api/v1/users/<USER_ID> \
  -H "Authorization: Bearer <TOKEN>" | jq

# Refresh token
curl -s -X POST http://localhost:8000/api/v1/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken": "<REFRESH_TOKEN>"}' | jq

# Forgot password
curl -s -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}' | jq

# Reset password
curl -s -X POST http://localhost:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "<RESET_TOKEN>", "password": "NewPass1!"}' | jq

# Delete user
curl -s -X DELETE http://localhost:8000/api/v1/users/<USER_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

### 8.6 Run lint / type-check

```bash
pip install ruff mypy
ruff check src/
mypy src/ --ignore-missing-imports
```

---

## Route Map After Changes

| Method | Path | Feature | Auth Required |
|--------|------|---------|---------------|
| `GET` | `/` | Root | No |
| `GET` | `/health` | Health | No |
| `GET` | `/health/live` | K8s liveness | No |
| `GET` | `/health/ready` | K8s readiness | No |
| `POST` | `/api/v1/login` | Auth | No |
| `POST` | `/api/v1/register` | Auth | No |
| `POST` | `/api/v1/refresh` | Auth | No (refresh token) |
| `POST` | `/api/v1/auth/forgot-password` | Password | No |
| `POST` | `/api/v1/auth/reset-password` | Password | No |
| `GET` | `/api/v1/users/{id}` | User CRUD | Yes |
| `DELETE` | `/api/v1/users/{id}` | User CRUD | Yes |

---

## Risks & Follow-Up Tasks

### Addressed in this plan
- Exception handler imports — `UserAlreadyExistsError` and `UserNotFoundError` created in domain exceptions to match what `exception_handlers.py` expects
- `alembic/env.py` config key — fixed from `"postgres"` to `"persistence.postgres"`
- `SECRET_KEY` length — updated to ≥32 chars in `.env`
- `slowapi` dependency — added to `requirements.txt`
- `role` persistence — added to `UserRepositoryImpl.save()` and `update()`
- Duplicate `POST /register` — removed from `user_routes.py` (auth feature is canonical)
- `user_repository_impl.py` broken `src.shared.domain.repositories.base_repository` import — deleted (unused)

### Left as follow-up (not blocking)
- **SlowAPIMiddleware**: Needs registration in `app.py` for rate limiting to actually enforce limits. Currently `@limiter.limit()` decorators run but are no-ops without the middleware
- **Correlation ID middleware**: Exists in `shared/logging/correlation.py` but needs wiring into `app.py` via `app.add_middleware()`
- **Request logging middleware**: Exists in `shared/infrastructure/middleware/request_logging_middleware.py` but not yet wired
- **`passlib` dependency**: Still in `requirements.txt` but unused. Remove after verification
- **`python-jose` + `psycopg2-binary`**: Unused dependencies — can be cleaned up separately
- **User routes auth enforcement**: `GET /api/v1/users/{id}` and `DELETE /api/v1/users/{id}` currently have no auth guard. Wire `Depends(get_current_user)` from `auth_dependencies.py` in a follow-up
