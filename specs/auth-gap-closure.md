# Auth Gap Closure: FE Integration Readiness

> **Status: ✅ Implemented** — June 2026
>
> Closes gaps identified in auth feature analysis to make the API fully ready for frontend integration
> (user CRUD, register, password reset, user sessions, JWT tokens).

---

## Goal

Make every auth and user endpoint production-ready for a React/Vite frontend to consume.
The FE needs: register, login, auto-refresh, logout, current user, profile update, password change,
password reset flow, and admin user CRUD — all with proper auth enforcement.

---

## Phase 1 — Critical Security Fixes

### 1.1 Fix broken import in `router_registry.py`

**Problem:** Line 10 imports from bare `app.features...` instead of `src.app.features...`.
If not running from project root, this breaks.

**Fix:** Change `app.features.user.presentation.user_routes` to `src.app.features.user.presentation.user_routes`.

**File:** `src/app/shared/presentation/router_registry.py`

### 1.2 Wire auth guards to user CRUD routes

**Problem:** `get_current_user` and `require_admin` dependencies exist in `auth_dependencies.py` but are completely unused. All CRUD operations on `/api/v1/users` are public.

**Fix:**
- `GET /api/v1/users/` → requires `Depends(get_current_user)` (any authenticated user can list)
- `GET /api/v1/users/{id}` → requires `Depends(get_current_user)` (any authenticated user can view)
- `POST /api/v1/users/` → requires `Depends(require_admin)` (admin-only create)
- `PUT /api/v1/users/{id}` → requires `Depends(require_admin)` (admin-only update)
- `DELETE /api/v1/users/{id}` → requires `Depends(require_admin)` (admin-only delete)

Also add import of `get_current_user` and `require_admin` from `src.app.shared.presentation.auth_dependencies`.

**File:** `src/app/features/user/presentation/user_routes.py`

---

## Phase 2 — Missing Endpoints for FE Integration

### 2.1 Add `GET /api/v1/users/me` (current user profile)

**Need:** After login, the FE needs to fetch current user profile for auth state sync, profile display, and session validation.

**New endpoint in `user_routes.py`:**
```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
) -> UserResponse:
    return await use_case.execute(str(current_user["sub"]))
```

### 2.2 Add `POST /api/v1/auth/logout`

**Need:** FE needs to invalidate the current session. Without this, a leaked access token grants access until the 15-minute expiry.

**Approach:** Store the access token's JTI in the `TokenRevocationService` (same in-memory store as refresh tokens). The `get_current_user` dependency checks revocation before accepting.

**Changes:**
- `JWTHandler.create_access_token()` — add `jti` claim (UUID4 per token)
- `TokenRevocationService` — already supports arbitrary token strings
- New logout endpoint in `auth_routes.py`:
  ```python
  @router.post("/logout", status_code=204)
  async def logout(
      request: Request,
      current_user: dict = Depends(get_current_user),
  ):
      token_revocation = get_token_revocation_service()
      await token_revocation.revoke_token(current_user["jti"], ttl_minutes=15)
  ```
- `auth_dependencies.py` `get_current_user()` — check `is_revoked(jti)` before accepting token

### 2.3 Add `POST /api/v1/auth/change-password`

**Need:** Authenticated users must be able to change their password without going through the forgot-password flow.

**New use case:** `ChangePasswordUseCase` in `src/app/features/auth/application/use_cases/change_password.py`

**New endpoint in `auth_routes.py`:**
```python
@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
):
```

**DTOs added to `auth_dto.py`:**
- `ChangePasswordRequest` — `current_password`, `new_password`
- `ChangePasswordResponse` — `message`

---

## Phase 3 — Security Hardening

### 3.1 ForgotPassword: remove token from response + hide user existence

**Problem 1:** `ForgotPasswordResponse` includes the raw reset token in the API response. This is a security risk — the token should be sent via email, not over the API channel.

**Problem 2:** Returning 404 for unknown emails enables email enumeration.

**Fix:**
- Remove `token` field from `ForgotPasswordResponse`
- On unknown email, return the same success response (don't disclose whether the email exists)
- Keep `token` generation unchanged (it still needs to be stored) — but note: without an email service, the token is currently unrecoverable. For local development, log the reset token (in non-prod envs only).
- Modify `forgot_password.py` `execute()`: don't raise `UserNotFoundError` — return success response with a generic message.

### 3.2 Register `SlowAPIMiddleware` in `app.py`

**Problem:** Rate limit decorators (`@limiter.limit()`) on login/register/refresh don't enforce without the middleware.

**Fix:** In `app.py`, add:
```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.app.shared.infrastructure.rate_limit.rate_limiter import limiter

fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
fastapi_app.add_middleware(SlowAPIMiddleware)
```

### 3.3 Add rate limiting to password endpoints

**Fix:** Add `@limiter.limit("3/minute")` to `forgot_password` and `@limiter.limit("5/minute")` to `reset_password` in `password_routes.py`.

---

## Phase 4 — Frontend Token Management Improvements

### 4.1 Add `expires_in` to login/register/refresh responses

**Need:** The FE needs to know when to refresh the access token proactively.

**Fix:** Add `expires_in: int` (seconds) field to:
- `AdminLoginResponse`
- `RefreshTokenResponse`
- Update `auth_mapper.py` `to_login_response()` to include `expires_in`
- Update `RefreshTokenUseCase` to include `expires_in` in its response

The value comes from `jwt_handler.expiration_minutes * 60`.

### 4.2 Remove duplicate `token` field from `AdminLoginResponse`

**Problem:** Both `token` and `access_token` contain the same JWT. Confusing for FE developers.

**Fix:**
- Remove `token` from `AdminLoginResponse`
- Update `auth_mapper.py` to not set `token`
- Keep only `access_token` and `refresh_token`

---

## Phase 5 — Error Response Standardization

### 5.1 Add structured error codes

**Problem:** All errors return `{"detail": "some string"}` — the FE must parse human-readable strings to handle errors programmatically.

**Fix:** Add an `error_code` field to error responses. Create an error response model:

```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    model_config = ConfigDict(extra="ignore")
```

**Error code constants** (to add in `src/app/shared/presentation/error_codes.py`):
| Code | HTTP | Meaning |
|------|------|---------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `AUTH_TOKEN_EXPIRED` | 401 | Access/refresh token expired |
| `AUTH_TOKEN_INVALID` | 401 | Malformed or revoked token |
| `AUTH_ACCOUNT_LOCKED` | 429 | Too many failed attempts |
| `AUTH_INSUFFICIENT_PERMISSIONS` | 403 | Role check failed |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `CONFLICT_EMAIL_EXISTS` | 409 | Duplicate email |
| `NOT_FOUND_USER` | 404 | User not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

Update `exception_handlers.py` to include `error_code` in all responses.

---

## Phase 6 — User Model & Auth Dependency Improvements

### 6.1 Add `is_active` field to UserModel

**Need:** Admin needs to disable accounts without deleting them. Also needed for email verification flow (future).

**Changes:**
- `UserModel` — add `is_active = Column(Boolean, default=True, nullable=False)`
- `UserEntity` — add `_is_active` field with property
- `UserModelMapper` — map the field
- New alembic migration: `alembic revision --autogenerate -m "add_is_active_to_users"`
- `LoginUserUseCase` — check `is_active` before allowing login
- `UserRepositoryImpl.update()` — persist `is_active`
- `UserUpdateRequest` — add optional `is_active: bool = None`

### 6.2 Check user existence in `get_current_user`

**Problem:** Deleted users retain active JWT tokens. The dependency only validates the JWT cryptographically and never checks if the user still exists.

**Fix:** In `get_current_user()`, after decoding the token, query the DB to verify the user exists and is active. If not found, return 401.

```python
user_repo = UserRepositoryImpl(session)  # get session from Depends
user = await user_repo.find_by_id(EntityId.from_string(payload["sub"]))
if not user or not user.is_active:
    raise UnauthorizedError("User no longer active")
```

---

## Phase 7 — Middleware & Cors

### 7.1 Load CORS origins from config YAML

**Problem:** CORS origins are retrieved from config but with hardcoded fallback. The config files don't have a `security.cors_origins` key.

**Fix:**
- Add `cors_origins` to all `config_*.yml` files under `security:` section
- For local: `["http://localhost:5173", "http://localhost:3000", "http://localhost:*"]`
- For container: `["http://localhost:5173", "http://localhost:*"]`
- The `app.py` code already reads from config — just needs the config entries

### 7.2 Wire `CorrelationIdMiddleware`

**Problem:** Middleware class exists in `shared/logging/correlation.py` but is never registered.

**Fix:** In `app.py`, after CORS middleware:
```python
from src.app.shared.logging.correlation import CorrelationIdMiddleware
fastapi_app.add_middleware(CorrelationIdMiddleware)
```

---

## Phase 8 — Dependency Cleanup

Remove unused packages from `requirements.txt`:
- `passlib[bcrypt]==1.7.4` (not imported — bcrypt used directly)
- `python-jose[cryptography]==3.4.0` (not imported — PyJWT used instead)
- `psycopg2-binary==2.9.10` (not imported — asyncpg is the async driver)

---

## Route Map After All Changes

| Method | Path | Auth Required | Role |
|--------|------|:---:|------|
| `GET` | `/` | No | — |
| `GET` | `/health`, `/health/live`, `/health/ready` | No | — |
| `POST` | `/api/v1/register` | No | — |
| `POST` | `/api/v1/login` | No | — |
| `POST` | `/api/v1/refresh` | No (refresh token) | — |
| `POST` | `/api/v1/logout` | **Yes** | any |
| `POST` | `/api/v1/auth/forgot-password` | No | — |
| `POST` | `/api/v1/auth/reset-password` | No | — |
| `POST` | `/api/v1/auth/change-password` | **Yes** | any |
| `GET` | `/api/v1/users/me` | **Yes** | any |
| `GET` | `/api/v1/users/` | **Yes** | any |
| `GET` | `/api/v1/users/{id}` | **Yes** | any |
| `POST` | `/api/v1/users/` | **Yes** | admin |
| `PUT` | `/api/v1/users/{id}` | **Yes** | admin |
| `DELETE` | `/api/v1/users/{id}` | **Yes** | admin |

---

## Verification Checklist

- [ ] `python3 -c "from src.main import app; print('import OK')"` passes
- [ ] `POST /register` returns access_token + refresh_token + expires_in (no duplicate `token`)
- [ ] `POST /login` returns access_token + refresh_token + expires_in
- [ ] `POST /refresh` returns new access_token + refresh_token + expires_in
- [ ] `POST /logout` succeeds with valid token, subsequent requests fail with 401
- [ ] `GET /users/me` returns current user profile
- [ ] `POST /auth/change-password` updates password, old password no longer works
- [ ] `POST /auth/forgot-password` returns generic success (no token in response, no 404 for unknown email)
- [ ] `GET /users/` returns 401 without auth, works with valid token
- [ ] `POST /users/` returns 403 for viewer, works for admin
- [ ] `PUT /users/{id}` returns 403 for viewer, works for admin
- [ ] `DELETE /users/{id}` returns 403 for viewer, works for admin
- [ ] Rate limiting enforced on login, register, refresh, forgot/reset-password
- [ ] Deleting a user invalidates their active JWT
- [ ] Inactive user cannot login
- [ ] Error responses include `error_code` field
