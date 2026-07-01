# Repository Standards

Repository-specific standards for making safe, minimal changes in this codebase.

## Architecture Boundaries

- Keep feature logic inside its feature package in `src/app/features/*`; avoid leaking feature-specific code into `src/app/shared/*`.
- Presentation layer (routes/DTOs/dependencies) stays in `presentation/`; use cases stay in `application/`; persistence/adapters stay in `infrastructure/`.
- Preserve central router registration in `src/app/shared/presentation/router_registry.py` instead of mounting routers ad hoc.

## Clean Code Practices

### Use Case Design

**Follow Command Pattern with DTOs:**
- Use case methods should accept DTOs (e.g., `UserCreateRequest`) rather than many individual parameters
- Keep context parameters separate (e.g., `user_id: str`)
- Maximum 2-3 parameters per use case method (typically: DTO + context ID)

**Parameter naming:**
- Use `payload` for input DTOs (matches `XxxRequest` type name)
- Use explicit ID names: `user_id` (not generic `id`)

**Example:**
```python
# ✅ Good
async def execute(self, payload: UserCreateRequest) -> UserResponse:
    pass

# ❌ Bad (too many params)
async def execute(self, email: str, password: str, first_name: str, ...) -> UserResponse:
    pass
```

### Route Handler Patterns

**Pass DTOs directly to use cases:**
```python
# ✅ Good - pass DTO directly
use_case.execute(payload)

# ❌ Bad - manual unpacking
use_case.execute(
    email=payload.email,
    password=payload.password,
    first_name=payload.first_name,
    # ... many lines
)
```

- Use self-documenting names that match their type or purpose
- Avoid generic names: `command`, `data`, `tmp`, `val`
- Match DTO type names: `UserCreateRequest` → `payload`
- Be explicit with IDs and context variables

### Variable Naming

- Use self-documenting names that match their type or purpose
- Avoid generic names: `command`, `data`, `tmp`, `val`
- Match DTO type names: `UserCreateRequest` → `payload`
- Be explicit with IDs and context variables

## API Contract Rules

- Keep endpoint versioning under the prefixes defined in `src/app/shared/presentation/router_registry.py` (`/api/v1` for auth, `/api/v1/users` for users).
- DTOs use `camelCase` for JSON via `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)`.

## Data and Migration Constraints

- For model/schema changes, update SQLAlchemy models and create Alembic migrations (`alembic revision --autogenerate -m "..."`, then `alembic upgrade head`).
- Maintain startup compatibility with container flow that expects migrations to succeed before Gunicorn starts (`scripts/start-api.sh`).

### SQLAlchemy Model Column Ordering

**Convention: `id → data → audit`**

Every table must follow this column order. Import `Base` from `src.app.shared.persistence`:

```python
from src.app.shared.persistence import Base
import uuid

class XxxModel(Base):
    __tablename__ = "xxx"

    # 1. Primary key (always first)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 2. Data columns (business fields, foreign keys, enums)
    name = Column(...)
    client_id = Column(UUID(as_uuid=True), ForeignKey(...))
    status = Column(...)

    # 3. Audit columns (always last)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True
    )
```

**Rationale:** `id` first for quick identification. Audit columns last because they are metadata, not business data. SQLAlchemy places parent class columns before child class columns, so `id`, `created_at`, and `updated_at` must be defined **explicitly on each concrete model** — not inherited from a base model.

**Rules:**
- ❌ Do not use an abstract base model with `id`, `created_at`, or `updated_at` — inheritance forces them first in column order
- ✅ Define `id`, `created_at`, and `updated_at` explicitly on each concrete model
- ✅ `id` always first, `created_at`/`updated_at` always last
- ✅ Use `Base = declarative_base()` (without abstract columns) as the shared parent

## Testing Strategy

No test suite exists yet. When implementing tests:

- Structure under `src/tests/` (`unit/`, `integration/`)
- Use `pytest-asyncio` for async test support
- Mock repository interfaces for unit tests; use real DB for integration tests

## Deployment Notes

- Docker service exposes API on `:8080` (`compose.yml`) while local `uvicorn src.main:app --reload` serves on `:8000`; verify the correct base URL in tests/docs.
- Container runtime entrypoint is `src.main:app` via Gunicorn (`scripts/start-api.sh`), not direct `uvicorn` module execution.

## Refactoring Guidelines

### When Refactoring Use Cases

1. **Check parameter count** - If > 4 parameters, refactor to use DTO
2. **Use existing DTOs** - Most features have `CreateXxxRequest` and `UpdateXxxRequest` DTOs
3. **Keep context separate** - Authentication/authorization context stays as separate params
4. **Update routes** - Change route handlers to pass DTOs directly (no unpacking)
5. **Verify** - Run `ruff check src/ && ruff format src/` to ensure no regressions

### Repository Pattern Consistency

- All repositories use plain `ABC` with explicit methods (no `BaseRepository`)
- Return types should match domain needs (e.g., `Tuple[ProjectEntity, str]` for project + client name)
- Repository methods use domain entities, not DTOs or models directly

### Mapper Patterns

Two layers of mappers, both in feature-local `mappers/` directories:

**Infrastructure mappers** (`infrastructure/mappers/`): Model ↔ Entity

Standalone `XxxMapper` class with `@staticmethod` methods. Models never carry mapping logic.

```python
# ✅ Good — standalone mapper class
class ClientMapper:
    @staticmethod
    def to_entity(model: ClientModel) -> ClientEntity: ...
    @staticmethod
    def to_model(entity: ClientEntity) -> ClientModel: ...

# ❌ Bad — mapping methods on the model
class ClientModel(Base):
    def to_entity(self) -> ClientEntity: ...    # model shouldn't know about domain
    def from_entity(cls, entity) -> "ClientModel": ...
```

Repository implementations call `XxxMapper.to_entity(model)` and `XxxMapper.to_model(entity)`.

**Application mappers** (`application/mappers/`): Entity ↔ DTO

Standalone functions. Naming: `to_xxx_response(entity, ...)` (match the DTO name). DTOs never carry mapping logic.

```python
# ✅ Good — standalone function
def to_project_response(entity: ProjectEntity, client_name: str, ...) -> ProjectResponse: ...

# ❌ Bad — mapping classmethod on the DTO
class ProjectResponse(BaseModel):
    @classmethod
    def from_entity(cls, entity, ...) -> "ProjectResponse": ...
```

**Rules:**
- ❌ Models must not have `to_entity()` / `from_entity()` methods
- ❌ DTOs must not have `from_entity()` / `to_response()` classmethods
- ❌ Routes must not construct DTOs inline — delegate to application mappers
- ❌ Use cases must not construct DTOs inline — delegate to application mappers
- ✅ Mappers live in the feature they serve (not in `shared/`)
- ✅ Keep mapper files focused — one mapper class/function per concern

### Validation Patterns

**Use shared validators, not wrapper methods:**

```python
# ✅ Good - Direct call to shared validators
class ProjectEntity:
    def update_details(self, name: str):
        ProjectValidators.validate_name(name)
        self._name = name

# ❌ Bad - Unnecessary wrapper methods
class ProjectEntity:
    @staticmethod
    def _validate_name(name: str):
        ProjectValidators.validate_name(name)  # Just passes through

    def update_details(self, name: str):
        self._validate_name(name)  # Extra indirection
```

**Why:** Wrappers add no value, bloat code, and obscure intent. Call validators directly.

**Reference:** The `user` feature uses domain value objects (`Password`, `Email`) for validation rather than a separate validators module.

### Dependency Injection Patterns

**Composition Root:**

All application dependencies are centrally managed in `src/app/composition/`:

```python
# ✅ Good - Import from composition root
from src.app.composition import (
    get_database_session,
    get_create_user_use_case,
    get_user_repository,
)

@router.post("/")
async def create_user(
    payload: UserCreateRequest,
    use_case = Depends(get_create_user_use_case),
):
    return await use_case.execute(payload)
```

**Composition Structure:**
- `composition/__init__.py` — Public API exports all dependencies
- `composition/infrastructure.py` — Database session, JWT handler
- `composition/repositories.py` — Repository factories (User)
- `composition/features/auth.py` — Auth use case factories (login, register, refresh, password reset)
- `composition/features/users.py` — User use case factories (CRUD)

**Factory Pattern:**
- All factories return interface types, not implementations
- Repositories return `ABC` interfaces (e.g., `ProjectRepository`)
- Use cases return concrete use case classes
- Infrastructure services may use singleton pattern (e.g., AI service)

**FastAPI vs Plain Factories:**
- Use `async def` factories with `Depends(...)` for standard DI in routes and use case wiring
- Use `def` (synchronous) plain factories (e.g., `build_story_repository`) when FastAPI `Depends()` resolution is not available — typically in auth dependency closures or path-parameter-dependent authorization checks
- Both variants live in the same composition module; the plain factory is a thin wrapper that bypasses DI for constrained contexts

**Adding New Dependencies:**
1. Create factory function in appropriate composition module
2. Return interface type from factory (for repositories)
3. Export from `composition/__init__.py`
4. Import from `src.app.composition` in routes

**Reference:** See `src/app/composition/` for complete composition root implementation.

## Import Conventions

**No `__init__.py` files in `src/app/features/`:**

- This project uses implicit namespace packages (Python 3.3+)
- All feature folders under `src/app/features/` have no `__init__.py` files
- Always use explicit file-path imports:

```python
# ✅ Correct - full path to the module file
from src.app.features.user.application.use_cases.create_user import CreateUserUseCase
from src.app.features.user.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

# ❌ Wrong - no __init__.py means no package-level re-exports
from src.app.features.user.application.use_cases import CreateUserUseCase  # will fail
```

**Exception:** The `composition/` root and `shared/` root still use `__init__.py` for public API exports.

## Keep It Lean

- Document only what differs from global standards.
- Avoid duplicating global guidance.
