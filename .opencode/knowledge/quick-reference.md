# Quick Reference Guide

Fast lookup for common patterns and commands in this repository.

## 🚀 Common Commands

### Development
```bash
# Start local development
uvicorn src.main:app --reload        # API on :8000 with hot reload

# Database
docker compose up postgres -d
alembic upgrade head                 # Run migrations
```

### Quality
```bash
ruff check src/ --fix                # Lint auto-fix
ruff format src/                     # Format code
```

### Docker
```bash
# Build and run
docker compose up -d
docker compose logs -f app

# Database operations
docker compose exec app alembic upgrade head
docker compose exec postgres psql -U template-admin -d template-db
```

---

## 📁 Feature Structure (No `__init__.py`)

**Existing features:** `auth`, `user`

```
src/app/features/{feature}/
├── application/
│   ├── dtos/              # Request/Response DTOs
│   ├── mappers/           # Entity ↔ DTO conversion (standalone functions)
│   └── use_cases/         # Business orchestration
├── domain/
│   ├── entities/          # Business objects
│   ├── repositories/      # Repository interfaces (ABC)
│   ├── validators/        # Domain validation
│   └── value_objects/     # Immutable domain values
├── infrastructure/
│   ├── mappers/           # Model ↔ Entity conversion (standalone classes)
│   ├── models/            # SQLAlchemy models
│   └── repositories/      # Repository implementations
└── presentation/
    └── {feature}_routes.py # FastAPI routes
```

**Import convention:** Always use full file paths (no `__init__.py` re-exports)

```python
# ✅ Correct
from src.app.features.user.application.use_cases.create_user import CreateUserUseCase
from src.app.features.user.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

# ❌ Wrong (will fail)
from src.app.features.user.application.use_cases import CreateUserUseCase
```

---

## 🔧 Dependency Injection

### Import from Composition Root

```python
from src.app.composition import (
    get_database_session,
    get_user_repository,
    get_create_user_use_case,
    get_user_by_id_use_case,
)
```

### Route Pattern

```python
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
) -> UserResponse:
    try:
        return await use_case.execute(str(user_id))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## 📝 Use Case Pattern

```python
class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, payload: UserCreateRequest) -> UserResponse:
        # 1. Build domain value objects
        password_vo = Password(payload.password)
        password_hash = password_vo.hash()

        # 2. Map DTO → entity
        new_user_entity = to_user_entity(payload, password_hash)

        # 3. Check for duplicates
        existing = await self.user_repository.find_by_email(new_user_entity.email)
        if existing:
            raise UserAlreadyExistsError(str(new_user_entity.email))

        # 4. Persist
        created = await self.user_repository.save(new_user_entity)

        # 5. Return DTO (via application mapper)
        return to_user_response(created)
```

**Rules:**
- Single responsibility: one use case per action
- Constructor receives repository interfaces (ABCs)
- `execute` receives a DTO and returns a DTO
- Domain exceptions raised directly (handled by global exception handlers or route-level try/except)

---

## 🗂️ File Locations

| Concern | Location |
|---------|----------|
| API bootstrap | `src/app/app.py` |
| ASGI entrypoint | `src/main.py` |
| DI factories | `src/app/composition/` |
| DI infra (DB, JWT) | `src/app/composition/infrastructure.py` |
| DI repos | `src/app/composition/repositories.py` |
| DI auth | `src/app/composition/features/auth.py` |
| DI users | `src/app/composition/features/users.py` |
| Router registry | `src/app/shared/presentation/router_registry.py` |
| Config files | `src/app/config/config_{env}.yml` |
| Models | Feature: `infrastructure/models/`, Shared: `src/app/shared/infrastructure/models/` |
| Mappers (infrastructure) | Feature: `infrastructure/mappers/` (class: `XxxModelMapper`) |
| Mappers (application) | Feature: `application/mappers/` (function: `to_xxx_response`) |
| Migrations | `alembic/versions/` |
| Scripts | `scripts/` |
| Health checks | `src/app/shared/presentation/health_checks.py` (`/health`, `/health/live`, `/health/ready`) |
| Logging | `src/app/shared/logging/` (structured logging) |
| Exception handlers | `src/app/shared/presentation/exception_handlers.py` |

---

## 🔍 Finding Things

```bash
# Find all routes
find src/app/features -name "*routes*.py"

# Find all repositories
find src/app/features -path "*/repositories/*.py"

# Find use cases
find src/app/features -path "*/use_cases/*.py"

# Find DTOs
find src/app/features -path "*/dtos/*.py"

# Find mappers
find src/app/features -path "*/mappers/*.py"

# Check what's exported from composition
cat src/app/composition/__init__.py | grep "^from"
```

---

## 📦 Adding a New Feature

1. **Create structure:**
   ```bash
   mkdir -p src/app/features/{feature}/{application,domain,infrastructure,presentation}
   mkdir -p src/app/features/{feature}/application/{dtos,mappers,use_cases}
   mkdir -p src/app/features/{feature}/domain/{entities,exceptions,repositories,value_objects}
   mkdir -p src/app/features/{feature}/infrastructure/{mappers,models,repositories}
   ```

2. **Create domain (inside out):**
   - Entity: `domain/entities/{entity}_entity.py`
   - Value objects: `domain/value_objects/`
   - Repository interface: `domain/repositories/{entity}_repository.py`
   - Exceptions: `domain/exceptions/{entity}_exceptions.py`

3. **Create application layer:**
   - DTOs: `application/dtos/{entity}_dto.py`
   - Mapper: `application/mappers/{entity}_dto_mapper.py`
   - Use case: `application/use_cases/{action}_{entity}.py`

4. **Create infrastructure:**
    - Mapper: `infrastructure/mappers/{entity}_model_mapper.py` (class with `to_entity`/`to_model`)
    - Model: `infrastructure/models/{entity}_model.py`
    - Repository impl: `infrastructure/repositories/{entity}_repository_impl.py`

5. **Create presentation:**
   - Routes: `presentation/{feature}_routes.py`

6. **Wire dependencies:**
   - Create `src/app/composition/features/{feature}.py`
   - Export from `src/app/composition/__init__.py`
   - Register router in `src/app/shared/presentation/router_registry.py`

7. **Create migration:**
   ```bash
   alembic revision --autogenerate -m "Add {feature} table"
   alembic upgrade head
   ```

---

## 🧪 Testing Patterns

No test suite exists yet. Tests should follow these patterns:

### Unit Test (Mock Repository)

```python
@pytest.mark.asyncio
async def test_create_user():
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.find_by_email.return_value = None
    mock_repo.save.return_value = mock_entity

    use_case = CreateUserUseCase(mock_repo)
    result = await use_case.execute(payload)

    assert result.email == "test@example.com"
    mock_repo.save.assert_called_once()
```

### Integration Test (Real DB)

```python
@pytest.mark.integration
async def test_user_repository(db_session):
    repo = UserRepositoryImpl(db_session)
    entity = to_user_entity(payload, "hashed_pw")

    saved = await repo.save(entity)
    assert saved.id is not None

    found = await repo.find_by_id(saved.id)
    assert found.email == Email("test@example.com")
```

---

## 🔐 Environment Variables

```bash
# Required
APP_ENV=local                     # local, dev, container, prod, test
SECRET_KEY=<32+ chars>           # JWT secret
POSTGRES_PASSWORD=<password>     # Database password

# Database (in config YAML)
# persistence.postgres.username: template-admin
# persistence.postgres.host:     localhost
# persistence.postgres.port:     5432
# persistence.postgres.dbname:   template-db

# Logging (in config YAML)
# logging.level: INFO
# logging.format: json
# logging.outputs: [console, file]
```

---

## 🎯 Common Patterns

### DTO with Validation

```python
class UserCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)
    role: UserRole = UserRole.VIEWER
```

### Entity with Domain Logic

```python
@dataclass
class UserEntity:
    id: EntityId
    email: Email
    first_name: str
    last_name: str
    password_hash: str
    role: UserRole

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_password_reset_token(self, token_hash: str, expires_at: datetime) -> None:
        self.password_reset_token_hash = token_hash
        self.password_reset_expires_at = expires_at
```

### Repository Interface

```python
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: EntityId) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def find_all(self, skip: int, limit: int) -> List[UserEntity]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass
```

### Repository Implementation

```python
class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: UserEntity) -> UserEntity:
        try:
            model = UserModelMapper.to_model(user)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return UserModelMapper.to_entity(model)
        except OperationalError as e:
            await self.session.rollback()
            raise DatabaseConnectionError(str(e))
```

### Infrastructure Mapper (Model ↔ Entity)

```python
class UserModelMapper:
    """Maps between UserEntity and UserModel."""

    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=EntityId(model.id),
            email=Email(model.email),
            first_name=model.first_name,
            last_name=model.last_name,
            # ...
        )

    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id.value,
            email=str(entity.email),
            first_name=entity.first_name,
            last_name=entity.last_name,
            # ...
        )
```

### Application Mapper (Entity → DTO)

```python
def to_user_response(entity: UserEntity) -> UserResponse:
    return UserResponse(
        id=str(entity.id),
        email=str(entity.email),
        first_name=entity.first_name,
        last_name=entity.last_name,
        display_name=entity.display_name,
        role=entity.role.value,
        created_at=entity.created_at.isoformat(),
    )
```

---

## 📋 Code Review Checklist

- [ ] Uses DTOs for use case parameters (not many individual params)
- [ ] Imports from `src.app.composition` (not feature dependencies)
- [ ] Uses explicit file-path imports (no `__init__.py` re-exports)
- [ ] Repository returns interface type, not implementation
- [ ] Routes pass DTOs directly to use cases
- [ ] Use cases never construct DTOs inline — delegate to application mappers
- [ ] Models do NOT have `to_entity()` / `from_entity()` — use infrastructure mapper class
- [ ] DTOs do NOT have `from_entity()` classmethods — use application mapper function
- [ ] Infrastructure mappers are `XxxMapper` class with `@staticmethod` methods
- [ ] Application mappers are standalone `to_xxx_response()` functions
- [ ] Exception handling: specific catch blocks before generic `except Exception`
- [ ] Repository methods handle `OperationalError` with rollback
- [ ] Migration created if model changed

---

## 🐛 Troubleshooting

### Import Errors

```python
# If you see: ModuleNotFoundError: No module named 'src.app.features.user.application.use_cases'
# Check: Are you using package-level imports? (not allowed in features/)
# Fix: Use full file-path imports

# ✅ Correct
from src.app.features.user.application.use_cases.create_user import CreateUserUseCase
```

### Database Connection

```bash
# Check database is running
docker compose ps postgres

# Check connection
docker compose exec postgres psql -U template-admin -d template-db -c "SELECT 1;"

# View logs
docker compose logs postgres
```

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

### Test Failures

No test suite exists yet. Run lint checks instead:

```bash
ruff check src/
ruff format src/ --check
```

---

**Last Updated:** June 25, 2026
