# Common Tasks

Step-by-step guides for common development tasks in this repository.

---

## 🆕 Add a New Endpoint

### Scenario: Add `GET /api/v1/users/{user_id}/profile` endpoint

**1. Create DTO (if needed):**

```python
# src/app/features/user/application/dtos/user_dto.py

class UserProfileResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    role: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
```

**2. Create Use Case:**

```python
# src/app/features/user/application/use_cases/get_user_profile.py

class GetUserProfileUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> UserProfileResponse:
        entity_id = EntityId.from_string(user_id)
        user = await self.user_repository.find_by_id(entity_id)
        if not user:
            raise UserNotFoundError(user_id)
        return to_user_profile_response(user)
```

**3. Add Factory to Composition:**

```python
# src/app/composition/features/users.py

from src.app.features.user.application.use_cases.get_user_profile import GetUserProfileUseCase

def get_user_profile_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(user_repository=user_repo)
```

**4. Export from Composition:**

```python
# src/app/composition/__init__.py

from .features.users import (
    # ... existing
    get_user_profile_use_case,
)
```

**5. Add Route:**

```python
# src/app/features/user/presentation/user_routes.py

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID,
    use_case: GetUserProfileUseCase = Depends(get_user_profile_use_case),
) -> UserProfileResponse:
    try:
        return await use_case.execute(str(user_id))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## 🗃️ Add a New Database Field

### Scenario: Add `phone` field to User

**1. Update Model:**

```python
# src/app/features/user/infrastructure/models/user_model.py

class UserModel(Base):
    # ... existing columns
    phone = Column(String(20), nullable=True)  # NEW
```

**2. Update Entity:**

```python
# src/app/features/user/domain/entities/user_entity.py

@dataclass
class UserEntity:
    # ... existing fields
    phone: Optional[str] = None  # NEW
```

**3. Update Infrastructure Mapper:**

```python
# src/app/features/user/infrastructure/mappers/user_model_mapper.py

# In to_entity:
    phone=model.phone,  # NEW

# In to_model:
    phone=entity.phone,  # NEW
```

**4. Update DTOs & Application Mapper:**

```python
# src/app/features/user/application/dtos/user_dto.py

class UserResponse(BaseModel):
    # ... existing fields
    phone: Optional[str] = None  # NEW

# src/app/features/user/application/mappers/user_dto_mapper.py

# In to_user_response:
    phone=entity.phone,  # NEW
```

**5. Create Migration:**

```bash
alembic revision --autogenerate -m "Add phone field to users"
alembic upgrade head
```

---

## 🔄 Add a New Repository Method

### Scenario: Add `find_by_email` (already exists — shown as reference)

**1. Add to Interface:**

```python
# src/app/features/user/domain/repositories/user_repository.py

class UserRepository(ABC):
    @abstractmethod
    async def find_by_role(self, role: UserRole) -> List[UserEntity]:
        """Find all users with the given role."""
        pass
```

**2. Implement:**

```python
# src/app/features/user/infrastructure/repositories/user_repository_impl.py

async def find_by_role(self, role: UserRole) -> List[UserEntity]:
    try:
        result = await self.session.execute(
            select(UserModel).where(UserModel.role == role.value)
        )
        models = result.scalars().all()
        return [UserModelMapper.to_entity(m) for m in models]
    except OperationalError as e:
        await self.session.rollback()
        raise DatabaseConnectionError(str(e))
```

---

## 🧪 Add Tests

No test suite exists yet. To set up tests:

```bash
pip install pytest pytest-asyncio httpx
mkdir -p src/tests/{unit,integration}
```

### Unit Test Pattern

```python
# src/tests/unit/application/test_create_user.py

@pytest.mark.asyncio
async def test_create_user_success():
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.find_by_email.return_value = None
    mock_repo.save.return_value = mock_entity

    use_case = CreateUserUseCase(mock_repo)
    result = await use_case.execute(payload)

    assert result.email == "test@example.com"
    mock_repo.save.assert_called_once()
```

### Integration Test Pattern

```python
# src/tests/integration/test_user_repository.py

@pytest.mark.integration
async def test_save_and_find_user(db_session):
    repo = UserRepositoryImpl(db_session)
    entity = to_user_entity(payload, "hashed_pw")

    saved = await repo.save(entity)
    assert saved.id is not None

    found = await repo.find_by_id(saved.id)
    assert found.email == Email("test@example.com")
```

---

## 🔐 Add Authorization Check

### Scenario: Only admin can list users

```python
# src/app/features/user/presentation/user_routes.py

from src.app.shared.presentation.auth_dependencies import require_admin

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin),
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
) -> PaginatedResponse[UserResponse]:
    return await use_case.execute(skip=skip, limit=limit)
```

---

## 🐛 Debug Common Issues

### Import Error

```
ModuleNotFoundError: No module named 'src.app.features.user.application.use_cases'
```

**Cause:** Trying to import from package (no `__init__.py` in features/)

**Fix:** Use full file-path imports:

```python
# ❌ Wrong
from src.app.features.user.application.use_cases import CreateUserUseCase

# ✅ Correct
from src.app.features.user.application.use_cases.create_user import CreateUserUseCase
```

### Circular Import

```
ImportError: cannot import name 'X' from partially initialized module
```

**Cause:** Two modules importing each other at module level

**Fix:** Use lazy imports in composition root:

```python
def get_use_case():
    from src.app.features.user.application.use_cases.create_user import CreateUserUseCase
    return CreateUserUseCase(...)
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
```

---

**Last Updated:** June 25, 2026
