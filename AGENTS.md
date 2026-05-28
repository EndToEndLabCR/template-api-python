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
  - **Note**: `compose.yml` references `./start.sh` (not `scripts/start-api.sh`) — this path mismatch may cause boot failures in Docker

## Configuration

- **Env**: `APP_ENV` selects YAML config file (default: `dev`)
- Config files: `src/app/config/config_{env}.yml`
- Yaml supports `!ENV ${VAR}` syntax via `pyaml-env`
- `AppConfig` singleton loads `.env` first, then the env-specific YAML
- Available environments: `dev`, `local`, `docker`, `stage`, `prod`, `test`

## Database

- Async PostgreSQL via `asyncpg` + SQLAlchemy 2.0 async
- Connection from config: `postgres.*` section in YAML
- **Important**: `PostgresDbConnection` is instantiated per dependency call (`dependencies.py`) — creates a new engine pool per request
- Alembic for migrations (async mode in `alembic/env.py`):
  - `alembic upgrade head` — apply pending
  - `alembic revision --autogenerate -m "msg"` — new migration
- Base model: `declarative_base` → `BaseModel` with UUID pk (`uuid.uuid1`), `created_at`, `updated_at`

## Models & Mapping

| Layer | Class | File |
|-------|-------|------|
| SQLAlchemy model | `UserModel` (fields: `id`, `email`, `first_name`, `last_name`, `password_hash`, `password_reset_token_hash`, `password_reset_expires_at`, `created_at`, `updated_at`) | `src/app/features/infrastructure/models/user_model.py` |
| Domain entity | `UserEntity` | `src/app/features/domain/entities/user_entity.py` |
| Repository interface | `UserRepository` | `src/app/features/domain/repositories/user_repository.py` |
| Repository impl | `UserRepositoryImpl` | `src/app/features/infrastructure/repository/user_repository_impl.py` |
| Model↔Entity mapper | `user_model_mapper.py` | `src/app/features/infrastructure/repository/user_model_mapper.py` |

## API Routes

| Prefix | File |
|--------|------|
| `/v1/user` | `src/app/features/presentation/web/routes/user_routes.py` |
| `/api/v1` (auth) | `src/app/features/presentation/web/routes/auth_routes.py` |
| `/api/v1` (password) | `src/app/features/presentation/web/routes/password_routes.py` |

- Root `GET /` returns `{"message": "Welcome to the API"}`
- Health `GET /health` returns `"Ok"`
- Docs disabled when `APP_ENV` is not `local` or `container`

## Notable Quirks

- `.env` line 1 has a leading space (` APP_ENV=local`) — `python-dotenv` may read key as ` APP_ENV` instead of `APP_ENV`, causing `AppConfig` to fall back to `DEFAULT_ENVIRONMENT="dev"`
- `EntityId.generate()` uses `uuid.uuid4` but `BaseModel.id` defaults to `uuid.uuid1` — mismatch between domain and persistence layers
- `user_dto_mapper.py` creates `EntityId` via `EntityId.from_string(str(uuid4()))` instead of `EntityId.generate()` — another UUID inconsistency at the DTO mapping layer
- `user_management/` directory mirrors `features/` structure with full subdir tree (`application/`, `domain/`, `infrastructure/`) but is **empty** (no `.py` files anywhere) — unused skeleton
- `LoginResponse` endpoint (`auth_routes.py`) returns **hardcoded mock data** (`{"name": "Alonso"}`) — the real DB query is commented out
- Registered route prefixes are **inconsistent**: user routes use `/v1/user` while auth and password routes use `/api/v1` — leads to paths like `/v1/user/register` and `/api/v1/auth/forgot-password`
- Container `compose.yml` references `./start.sh` as the command, but the actual script is `scripts/start-api.sh` — the Dockerfile's `COPY` may not map `start.sh` to the root
- `PostgresDbConnection` is instantiated **per dependency call** (see `dependencies.py`), creating a new connection engine + pool on every request — should be a singleton or cached
- CORS origins are **hardcoded** in `app.py` (lines 25-27) — not loaded from config; only allows `localhost:5173` and `localhost:*`
- Dependencies: both `passlib[bcrypt]` and `bcrypt` in `requirements.txt`, but `passlib` is **unused** — password hashing is done directly via `bcrypt.hashpw()`
- Dependencies: both `asyncpg` and `psycopg2-binary` are listed, but only `asyncpg` is used for async PostgreSQL; `psycopg2-binary` appears unused
- Service layer delegates to UseCase classes (e.g., `CreateUserUseCase`, `GetUserByIdUseCase`)
- No tests, no CI, no pre-commit, no linter/formatter config in this repo

## Environment Variables

| Var | Default | Notes |
|-----|---------|-------|
| `APP_ENV` | `dev` | Selects config YAML |
| `POSTGRES_PASSWORD` | — | Referenced via `!ENV ${POSTGRES_PASSWORD}` in YAML |
| `SECRET_KEY` | — | Used in `.env` |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Gunicorn bind host |
| `PORT` | `8080` | Gunicorn bind port (8000 for uvicorn dev) |
| `GUNICORN_WORKERS` | `2` | Worker count |

## Retry Decorators

In `src/shared/utils/retry_decorator.py`:
- `retry_on_exception()` — exponential backoff, 3 retries, any Exception
- `retry_read_operation()` — SQLAlchemy/OperationalError, 3 retries, factor 1.5
- `retry_write_operation()` — +IntegrityError, 5 retries, factor 2.0
- `retry_critical_operation()` — any Exception, 7 retries, factor 2.5
