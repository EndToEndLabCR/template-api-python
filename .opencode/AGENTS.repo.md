# Repository Agent Instructions

This file contains repository-specific rules and preferences.

## Scope

- Apply only to this repository.
- Do not duplicate global rules from ${HOME}/.config/opencode.

## Domain Boundaries

- Main API bootstrap is `src/app/app.py`; ASGI entrypoint for deployments is `src/main.py` (`app = fastapi_app`).
- Business code is feature-first under `src/app/features/{auth,user}` with layered folders (`application/`, `domain/`, `infrastructure/`, `presentation/`).
- Cross-feature concerns live under `src/app/shared/` and follow the same layered split; prefer shared modules only for true cross-feature reuse.
- API routers are centrally wired in `src/app/shared/presentation/router_registry.py`: auth routes at `/api/v1`, user routes at `/api/v1/users`.
- **Dependency injection** is centralized in `src/app/composition/` — all use cases, repositories, and infrastructure dependencies are exported from `composition/__init__.py`.
- **`__init__.py` files:** Feature folders under `src/app/features/` use implicit namespace packages (no `__init__.py`). Always use explicit file-path imports. The `composition/` and `shared/` roots retain `__init__.py` for public API exports.
- **Health check endpoints:** `/health` (combined check), `/health/live` (liveness probe), `/health/ready` (readiness probe) — all registered via `src/app/shared/presentation/health_checks.py`.

## Build, Test, and Run Commands

- Install: `pip install -r requirements.txt`
- Run API locally: `uvicorn src.main:app --reload --port 8000`
- Run in Docker: `docker compose up --build -d` (API on :8080)
- No test suite exists yet. Run lint checks: `ruff check src/ && ruff format src/ --check`

## Quality Verification

**After making any code changes, run these commands to verify quality:**

1. **Linting**: `ruff check src/` (check) or `ruff check src/ --fix` (auto-fix)
2. **Formatting**: `ruff format src/` (format) or `ruff format src/ --check` (verify)
3. **Verify app starts**: `uvicorn src.main:app` (smoke test)

**Verification workflow:**
```bash
ruff check src/ --fix && ruff format src/ && uvicorn src.main:app
```

## Data, Security, and Environment Constraints

- Configuration is environment-driven via `APP_ENV` and `src/app/config/config_<env>.yml`; loaded by `src/app/config/app_config.py`.
- Supported environments: `local`, `dev`, `container`, `prod`, `test` (each with corresponding `config_<env>.yml`).
- Docker startup: `scripts/start-api.sh` runs `alembic upgrade head` then starts gunicorn.
- In non-local/non-test environments, API docs are disabled (`docs_url`, `redoc_url`, `openapi_url` set to `None` in `app.py`).
- CORS origins are loaded from config YAML (`security.cors_origins`), falling back to hardcoded defaults.
- The `.env.example` file documents required environment variables (`APP_ENV`, `SECRET_KEY`, `POSTGRES_PASSWORD`).

## Naming Conventions (Quick Reference)

**Use case parameters:**
- `payload: UserCreateRequest` (DTO for input)
- `user_id: str` (explicit IDs, not generic `id`)

**Variable names:**
- ❌ Generic: `command`, `data`, `tmp`, `val`
- ✅ Self-documenting: `payload`, `user_count`, `user_id`

**Comments:**
- Explain WHY, not WHAT
- Only for non-obvious logic

See `.opencode/knowledge/repo-standards.md` for detailed implementation patterns.
