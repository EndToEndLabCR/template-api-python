# AGENTS.md — template-api-python

## Architecture

Clean Architecture + DDD — 4 layers under `src/`:

| Layer | Location | Purpose |
|-------|----------|---------|
| Domain | `src/shared/domain/`, `src/app/features/*/domain/` | Entities, value objects, repository interfaces. Zero external deps. |
| Application | `src/app/features/*/application/` | Use cases, DTOs, services, exceptions. Depends only on Domain. |
| Infrastructure | `src/shared/infrastructure/`, `src/app/features/*/infrastructure/` | DB models, repository impls, DB connection. |
| Presentation | `src/app/features/*/presentation/` | FastAPI routes, dependencies. |

Cross-cutting code lives in `src/shared/` (utils, domain base classes, db connection).

## Entrypoint & Running

- **App entrypoint**: `src/main:app` — FastAPI app built in `src/app/app.py`
- **Local dev**: `uvicorn src.main:app --reload` (port 8000)
- **Docker**: `docker compose up --build -d` (port 8080)
- **Gunicorn**: `gunicorn -k uvicorn.workers.UvicornWorker -c ./src/app/gunicorn_conf.py src.main:app`
- Container entrypoint: `scripts/start-api.sh` — runs `alembic upgrade head` then gunicorn

## Configuration

- **Env**: `APP_ENV` selects YAML config file (default: `dev`)
- Config files: `src/app/config/config_{env}.yml`
- Yaml supports `!ENV ${VAR}` syntax via `pyaml-env`
- `AppConfig` singleton loads `.env` first, then the env-specific YAML
- Available environments: `local`, `dev`, `container`, `prod`, `test`

## Database

- Async PostgreSQL via `asyncpg` + SQLAlchemy 2.0 async
- Connection from config: `persistence.postgres.*` section in YAML
- Engine is a singleton via `engine_factory.get_engine()` — no per-request pool creation
- Alembic for migrations (async mode in `alembic/env.py`):
  - `alembic upgrade head` — apply pending
  - `alembic revision --autogenerate -m "msg"` — new migration
- Models inherit from `Base` (declarative_base) and define all columns explicitly

## Models & Mapping

| Layer | Class | File |
|-------|-------|------|
| SQLAlchemy model | `UserModel` (fields: `id`, `email`, `first_name`, `last_name`, `role`, `is_active`, `password_hash`, `password_reset_token_hash`, `password_reset_expires_at`, `created_at`, `updated_at`) | `src/app/features/user/infrastructure/models/user_model.py` |
| Domain entity | `UserEntity` | `src/app/features/user/domain/entities/user_entity.py` |
| Repository interface | `UserRepository` | `src/app/features/user/domain/repositories/user_repository.py` |
| Repository impl | `UserRepositoryImpl` | `src/app/features/user/infrastructure/repositories/user_repository_impl.py` |
| Model↔Entity mapper | `UserModelMapper` | `src/app/features/user/infrastructure/mappers/user_model_mapper.py` |

## API Routes

| Prefix | File |
|--------|------|
| `/api/v1` (login, register, refresh, logout, change-password) | `src/app/features/auth/presentation/auth_routes.py` |
| `/api/v1/auth` (forgot/reset password) | `src/app/features/auth/presentation/password_routes.py` |
| `/api/v1/users` (CRUD + /me) | `src/app/features/user/presentation/user_routes.py` |

- Root `GET /` returns `{"message": "Welcome to the API"}`
- Health `GET /health` returns `"Ok"`
- Docs disabled when `APP_ENV` is not `local` or `container`
- All user CRUD routes require authentication; `POST/PUT/DELETE` require admin role
- `GET /api/v1/users/me` returns the authenticated user's profile
- `POST /api/v1/logout` revokes the current access token via JTI blacklisting

## Notable Quirks

- `LoginResponse` uses `camelCase` for JSON (e.g., `accessToken`, `refreshToken`, `expiresIn`) via Pydantic `alias_generator=to_camel`
- `UserEntity.display_name` is a **computed property** (`f"{first_name} {last_name}"`) — not persisted in the database
- `EntityId.generate()` uses `uuid.uuid4`; both domain and model layers use UUID v4 consistently
- Service layer delegates to UseCase classes (e.g., `CreateUserUseCase`, `GetUserByIdUseCase`)
- `TokenRevocationService` and `AccountLockoutService` use in-memory storage — suitable for single-instance deployments; replace with Redis for multi-instance
- ForgotPassword always returns a generic success response to prevent email enumeration; the raw reset token is logged in dev/local envs only
- `ChangePasswordRequest` and `LoginRequest` DTOs use `camelCase` aliasing; `ForgotPasswordRequest` and `ResetPasswordRequest` also use camelCase
- No tests, no CI, no pre-commit, no linter/formatter config in this repo

## Environment Variables

| Var | Default | Notes |
|-----|---------|-------|
| `APP_ENV` | `dev` | Selects config YAML |
| `POSTGRES_PASSWORD` | — | Referenced via `!ENV ${POSTGRES_PASSWORD}` in YAML |
| `SECRET_KEY` | — | Used in `.env` for JWT signing |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Gunicorn bind host |
| `PORT` | `8080` | Gunicorn bind port (8000 for uvicorn dev) |
| `GUNICORN_WORKERS` | `2` | Worker count |

## Retry Decorators

In `src/app/shared/utils/retry_decorator.py`:
- `retry_on_exception()` — exponential backoff, 3 retries, any Exception
- `retry_read_operation()` — SQLAlchemy/OperationalError, 3 retries, factor 1.5
- `retry_write_operation()` — +IntegrityError, 5 retries, factor 2.0
- `retry_critical_operation()` — any Exception, 7 retries, factor 2.5
