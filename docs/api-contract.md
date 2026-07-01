# API Contract — template-api-python

> **Audience**: Frontend developers needing to integrate with this API.
> **Last updated**: 2026-06-26

---

## 1. Base URL & Conventions

| Item | Value |
|------|-------|
| **Prefix** | `/api/v1` |
| **Content-Type** | `application/json` for all request/response bodies |
| **Auth header** | `Authorization: Bearer <token>` |
| **Naming** | All JSON keys use **camelCase** (both request and response) |
| **Date/time** | ISO 8601 UTC with `Z` suffix, e.g. `"2026-06-26T10:00:00Z"` |

### CamelCase Mapping

| Python backend | JSON wire format |
|---------------|-----------------|
| `first_name` | `firstName` |
| `last_name` | `lastName` |
| `display_name` | `displayName` |
| `access_token` | `accessToken` |
| `refresh_token` | `refreshToken` |
| `expires_in` | `expiresIn` |
| `logged_in_at` | `loggedInAt` |
| `current_password` | `currentPassword` |
| `new_password` | `newPassword` |
| `is_active` | `isActive` |
| `error_code` | `error_code` | (preserves snake_case — not aliased) |

> **Note**: The `error_code` field in error responses and the pagination envelope fields (`total`, `page`, `per_page`) use **snake_case** — they are not aliased to camelCase. All other fields (request bodies, user/response objects) use camelCase.

---

## 2. Authentication Flow

### 2.1 Tokens

| Property | Access Token | Refresh Token |
|----------|-------------|---------------|
| **Algorithm** | HS256 | HS256 |
| **Lifetime** | 15 minutes | 7 days |
| **Claims** | `sub` (user UUID), `email`, `role`, `jti` (revocation ID) | `sub`, `email`, `role`, `type: "refresh"` |

### 2.2 Recommended Flow

```
1. POST /api/v1/login          → get accessToken + refreshToken
2. Store both tokens securely (httpOnly cookies or secure storage)
3. Attach accessToken to every request:  Authorization: Bearer <accessToken>
4. On 401, call POST /api/v1/refresh   → get new accessToken + new refreshToken
5. On refresh failure → redirect to login
6. On logout, call POST /api/v1/logout  → revokes current accessToken
```

> ⚠️ Refresh tokens are **single-use**. Each refresh call returns a new token pair and invalidates the old refresh token.

### 2.3 Roles

| Role | Value | Permissions |
|------|-------|-------------|
| `viewer` | `"viewer"` | Get own profile, list users, get user by ID, change own password |
| `admin` | `"admin"` | All viewer permissions + create/update/delete users |

New registrations default to `viewer`.

---

## 3. Error Response Format

All errors follow this structure:

```json
{
  "detail": "Invalid credentials",
  "error_code": "AUTH_INVALID_CREDENTIALS"
}
```

### Error Codes Reference

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `AUTH_TOKEN_EXPIRED` | 401 | Access/refresh token expired |
| `AUTH_TOKEN_INVALID` | 401 | Token malformed or invalid signature |
| `AUTH_TOKEN_REVOKED` | 401 | Token was revoked (logged out) |
| `AUTH_ACCOUNT_LOCKED` | 429 | Too many login failures — includes `Retry-After` header |
| `AUTH_ACCOUNT_INACTIVE` | 401 | User account deactivated |
| `AUTH_INSUFFICIENT_PERMISSIONS` | 403 | Missing required role |
| `NOT_FOUND` | 404 | Generic resource not found |
| `NOT_FOUND_USER` | 404 | User not found |
| `CONFLICT_EMAIL_EXISTS` | 409 | Email already registered |
| `VALIDATION_ERROR` | 400 / 422 | Invalid request body or query params |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `DATABASE_ERROR` | 503 | Database unreachable |

### Rate Limiting Summary

| Endpoint | Limit |
|----------|-------|
| `POST /login` | 10/min per IP |
| `POST /register` | 5/min per IP |
| `POST /refresh` | 10/15min per IP |
| `POST /change-password` | 5/min per IP |
| `POST /auth/forgot-password` | 3/min per IP |
| `POST /auth/reset-password` | 5/min per IP |
| All others | 100/min per IP (global default) |

---

## 4. Endpoints

### 4.1 Health Check

<details>
<summary><strong>GET /</strong></summary>

**Auth**: None

**Response** `200`:
```json
{
  "message": "Welcome to the API"
}
```
</details>

<details>
<summary><strong>GET /health</strong></summary>

**Auth**: None

**Success** `200`:
```json
{
  "status": "healthy",
  "service": "App API",
  "version": "1.0.0",
  "database": "connected"
}
```

**Failure** `503`:
```json
{
  "status": "unhealthy",
  "service": "App API",
  "version": "1.0.0",
  "database": "disconnected",
  "error": "database_unreachable"
}
```
</details>

<details>
<summary><strong>GET /health/live</strong></summary>

**Auth**: None

**Response** `200`:
```json
{
  "status": "alive",
  "service": "App API",
  "version": "1.0.0"
}
```
</details>

<details>
<summary><strong>GET /health/ready</strong></summary>

**Auth**: None

**Success** `200`:
```json
{
  "status": "ready",
  "service": "App API",
  "version": "1.0.0",
  "checks": { "database": "connected" }
}
```

**Failure** `503`:
```json
{
  "status": "not_ready",
  "service": "App API",
  "version": "1.0.0",
  "checks": { "database": "disconnected" },
  "error": "database_unreachable"
}
```
</details>

---

### 4.2 Auth Endpoints

#### POST /api/v1/login

**Auth**: None | **Rate limit**: 10/min

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss1"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `email` | string | ✅ | Valid email format |
| `password` | string | ✅ | — |

**Response** `200`:
```json
{
  "accessToken": "eyJhbGciOi...",
  "refreshToken": "eyJhbGciOi...",
  "expiresIn": 900,
  "email": "user@example.com",
  "displayName": "John Doe",
  "loggedInAt": "2026-06-26T10:00:00Z",
  "role": "viewer",
  "user": {
    "email": "user@example.com",
    "displayName": "John Doe",
    "name": "John Doe",
    "role": "viewer"
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| `accessToken` | string | JWT, 15-minute TTL |
| `refreshToken` | string | JWT, 7-day TTL |
| `expiresIn` | number | Seconds until access token expires (900 = 15 min) |
| `email` | string | User's email |
| `displayName` | string | Computed: `firstName lastName` |
| `loggedInAt` | string | ISO 8601 UTC |
| `role` | string | `"admin"` or `"viewer"` |
| `user` | object | Nested user summary |
| `user.name` | string | Same as `displayName` |

**Errors**: `401` (AUTH_INVALID_CREDENTIALS), `429` (AUTH_ACCOUNT_LOCKED or rate limit)

> 💡 The `expiresIn` field is in **seconds**. Set a timer to refresh the token before it expires.

> ⚠️ **Account lockout**: After 5 failed login attempts within a 30-minute window, the account is temporarily locked (returns `429` with `Retry-After` header). Failures on non-existent emails are counted too (to prevent user enumeration).

---

#### POST /api/v1/register

**Auth**: None | **Rate limit**: 5/min

**Request**:
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "SecureP@ss1",
  "role": "viewer"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `firstName` | string | ✅ | Min 1, max 50 chars |
| `lastName` | string | ✅ | Min 1, max 50 chars |
| `email` | string | ✅ | Valid email, max 255 chars |
| `password` | string | ✅ | See [password policy](#password-policy) |
| `role` | string | ❌ | `"admin"` or `"viewer"`. Default: `"viewer"` |

**Response** `201`: Same structure as [POST /login](#post-apiv1login) (auto-login: returns tokens immediately).

**Errors**: `400` (weak password or invalid email), `409` (CONFLICT_EMAIL_EXISTS), `429` (rate limit)

---

#### POST /api/v1/refresh

**Auth**: None | **Rate limit**: 10/15min

**Request**:
```json
{
  "refreshToken": "eyJhbGciOi..."
}
```

| Field | Type | Required |
|-------|------|----------|
| `refreshToken` | string | ✅ |

**Response** `200`:
```json
{
  "accessToken": "eyJhbGciOi...",
  "refreshToken": "eyJhbGciOi...",
  "expiresIn": 900
}
```

> ⚠️ **Single-use rotation**: The old refresh token is immediately revoked. Store the new pair and discard the old one.

**Errors**: `401` (token expired, invalid, or already used), `429` (rate limit)

---

#### POST /api/v1/logout

**Auth**: Bearer token required | **Rate limit**: default (100/min)

**Request**: No body — token extracted from `Authorization` header.

**Response** `200`:
```json
{
  "message": "Logged out successfully"
}
```

**Errors**: `401` (token invalid/expired/revoked)

---

#### POST /api/v1/change-password

**Auth**: Bearer token required | **Rate limit**: 5/min

**Request**:
```json
{
  "currentPassword": "OldP@ss1",
  "newPassword": "NewP@ss2"
}
```

| Field | Type | Required |
|-------|------|----------|
| `currentPassword` | string | ✅ |
| `newPassword` | string | ✅ (see [password policy](#password-policy)) |

**Response** `200`:
```json
{
  "message": "Password changed successfully"
}
```

**Errors**: `400` (weak new password), `401` (wrong current password or invalid auth)

---

#### POST /api/v1/auth/forgot-password

**Auth**: None | **Rate limit**: 3/min

**Request**:
```json
{
  "email": "user@example.com"
}
```

| Field | Type | Required |
|-------|------|----------|
| `email` | string | ✅ |

**Response** `200`:
```json
{
  "message": "If an account with that email exists, a password reset link has been sent."
}
```

> ⚠️ This endpoint **always** returns the same success response — regardless of whether the email exists. This prevents attackers from enumerating registered emails.

> 💡 In local/dev environments, the raw reset token is logged to the console for development convenience.

**Errors**: `400` (invalid email format), `500` (unexpected error)

---

#### POST /api/v1/auth/reset-password

**Auth**: None | **Rate limit**: 5/min

**Request**:
```json
{
  "token": "abc123rawtoken...",
  "password": "NewSecureP@ss1"
}
```

| Field | Type | Required |
|-------|------|----------|
| `token` | string | ✅ (raw reset token from forgot-password) |
| `password` | string | ✅ (see [password policy](#password-policy)) |

**Response** `200`:
```json
{
  "message": "Password has been reset successfully"
}
```

> 💡 Reset tokens are single-use and expire after 30 minutes.

**Errors**: `400` (invalid token, expired token, weak password), `429` (rate limit)

---

### 4.3 User Endpoints

#### POST /api/v1/users/

**Auth**: Bearer token (admin only) | **Rate limit**: default (100/min)

Creates a new user (admin-managed — does NOT auto-login).

**Request**: Same as [POST /register](#post-apiv1register) (all fields including `password`).

**Response** `201`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "firstName": "Jane",
  "lastName": "Smith",
  "displayName": "Jane Smith",
  "email": "jane@example.com",
  "role": "viewer"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | UUID v4 |
| `firstName` | string | — |
| `lastName` | string | — |
| `displayName` | string | Computed property (not stored) |
| `email` | string | — |
| `role` | string | `"admin"` or `"viewer"` |

**Errors**: `400` (validation), `401` (no auth), `403` (not admin), `409` (CONFLICT_EMAIL_EXISTS)

> ℹ️ Unlike `/register`, this endpoint **does not** return tokens — it only returns the created user.

---

#### GET /api/v1/users/

**Auth**: Bearer token (any role) | **Rate limit**: default (100/min)

List users with pagination.

**Query Parameters**:

| Parameter | Type | Default | Constraints |
|-----------|------|---------|-------------|
| `skip` | integer | `0` | ≥ 0 |
| `limit` | integer | `20` | ≥ 1, ≤ 100 |

**Response** `200`:
```json
{
  "total": 42,
  "page": 1,
  "per_page": 20,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "firstName": "John",
      "lastName": "Doe",
      "displayName": "John Doe",
      "email": "john@example.com",
      "role": "viewer"
    }
  ]
}
```

| Field | Type | Notes |
|-------|------|-------|
| `total` | number | Total items in the collection |
| `page` | number | 1-indexed page number |
| `per_page` | number | Items per page (1-100) |
| `items` | array | Array of UserResponse objects |

**Errors**: `401` (no auth), `404` (no users found)

---

#### GET /api/v1/users/me

**Auth**: Bearer token (any role) | **Rate limit**: default (100/min)

Returns the profile of the currently authenticated user (identified by the JWT).

**Response** `200`: Same as [UserResponse](#user-response).

**Errors**: `400` (invalid user ID in token), `401` (no auth), `404` (user not found)

---

#### GET /api/v1/users/{user_id}

**Auth**: Bearer token (any role) | **Rate limit**: default (100/min)

Get a single user by UUID.

**Path Parameters**:

| Parameter | Type |
|-----------|------|
| `user_id` | UUID v4 |

**Response** `200`: Same as [UserResponse](#user-response).

**Errors**: `400` (invalid UUID), `401` (no auth), `404` (NOT_FOUND_USER)

---

#### PUT /api/v1/users/{user_id}

**Auth**: Bearer token (admin only) | **Rate limit**: default (100/min)

Update an existing user.

**Request**:
```json
{
  "firstName": "Updated",
  "lastName": "Name",
  "email": "updated@example.com",
  "role": "viewer",
  "isActive": true
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `firstName` | string | ✅ | Min 1, max 50 |
| `lastName` | string | ✅ | Min 1, max 50 |
| `email` | string | ✅ | Valid email, max 255 |
| `role` | string | ✅ | `"admin"` or `"viewer"` |
| `isActive` | boolean\|null | ❌ | `null` = preserve existing value. Default: `null` |

> ℹ️ Passwords are **not** updated via this endpoint. Use `POST /change-password` instead.

**Response** `200`: Same as [UserResponse](#user-response).

**Errors**: `400` (validation), `401` (no auth), `403` (not admin), `404` (NOT_FOUND_USER)

---

#### DELETE /api/v1/users/{user_id}

**Auth**: Bearer token (admin only) | **Rate limit**: default (100/min)

Delete a user by UUID.

**Response**: `204 No Content` (empty body).

**Errors**: `400` (invalid UUID), `401` (no auth), `403` (not admin), `404` (NOT_FOUND_USER)

---

### 4.4 Endpoint Summary Table

| Method | Path | Auth | Role |
|--------|------|------|------|
| `GET` | `/` | ❌ | — |
| `GET` | `/health` | ❌ | — |
| `GET` | `/health/live` | ❌ | — |
| `GET` | `/health/ready` | ❌ | — |
| `POST` | `/api/v1/login` | ❌ | — |
| `POST` | `/api/v1/register` | ❌ | — |
| `POST` | `/api/v1/refresh` | ❌ | — |
| `POST` | `/api/v1/logout` | ✅ | any |
| `POST` | `/api/v1/change-password` | ✅ | any |
| `POST` | `/api/v1/auth/forgot-password` | ❌ | — |
| `POST` | `/api/v1/auth/reset-password` | ❌ | — |
| `POST` | `/api/v1/users/` | ✅ | admin |
| `GET` | `/api/v1/users/` | ✅ | any |
| `GET` | `/api/v1/users/me` | ✅ | any |
| `GET` | `/api/v1/users/{id}` | ✅ | any |
| `PUT` | `/api/v1/users/{id}` | ✅ | admin |
| `DELETE` | `/api/v1/users/{id}` | ✅ | admin |

---

## 5. Password Policy

Passwords must satisfy all of the following:

- Minimum **8 characters**
- At least **1 uppercase letter** `[A-Z]`
- At least **1 lowercase letter** `[a-z]`
- At least **1 digit** `[0-9]`
- At least **1 special character** from: ``!@#$%^&*(),.?":{}|<>_-+=[]\/`~'``

> Frontend should validate these rules client-side before submitting to avoid unnecessary `400` errors.

---

## 6. Computed Fields (Important for FE)

| Field | Source | Notes |
|-------|--------|-------|
| `displayName` | `firstName + " " + lastName` | Computed on every response — never stored in DB |
| `user.name` | Same as `displayName` | Present only in login/register responses |
| `loggedInAt` | Current server UTC time | Generated at response time, not persisted |

---

## 7. Anti-Enumeration Protections

The following endpoints deliberately avoid leaking whether an account exists:

- **`POST /auth/forgot-password`**: Always returns the same success message regardless of whether the email is registered.
- **`POST /login`**: Failed attempts on non-existent emails are tracked (to prevent timing-based user enumeration).

---

## 8. OpenAPI / Swagger Docs

The interactive API docs (Swagger UI / ReDoc) are only available when the environment is `local` or `test`. They are disabled in `dev`, `container`, and `prod`.

- Swagger UI: `{base_url}/docs`
- ReDoc: `{base_url}/redoc`

---

## 9. CORS

The API allows cross-origin requests from:

| Environment | Allowed Origins |
|-------------|----------------|
| `local` / `dev` | `http://localhost:5173`, `http://localhost:3000`, `http://localhost:*` |
| `container` | `http://localhost:5173`, `http://localhost:*` |
| `prod` | Empty (same-origin only) |
| `test` | Falls back to default (`http://localhost:5173`, `http://localhost:*`) |

Credentials (cookies / authorization headers) are allowed across origins.
