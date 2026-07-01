# Template API Project

This project serves as a template for building scalable and maintainable API services. It provides a structured foundation for developers to kickstart their projects with essential features and configurations. The primary purpose is to simplify the development process and ensure best practices are followed. Intended users include developers and teams working on API-based applications.

## 📑 Table of Contents

- [Template API Project](#template-api-project)
  - [📑 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🛠️ Technologies Used](#️-technologies-used)
  - [🚀 Getting Started](#-getting-started)
    - [⚙️ Prerequisites](#️-prerequisites)
    - [💾 Installation](#-installation)
    - [📝 Configuration](#-configuration)
    - [Pip](#pip)
    - [🏃 Running the App](#-running-the-app)
      - [🐳 Running with Docker](#-running-with-docker)
      - [🖥️ Running with PyCharm](#️-running-with-pycharm)
  - [🗄️ Database Management](#️-database-management)
    - [Creating Migrations](#creating-migrations)
    - [Running Migrations](#running-migrations)
  - [🌱 Seed Users](#-seed-users)
  - [📡 API Endpoints](#-api-endpoints)
  - [🤝 Contributing](#-contributing)

## ✨ Features

- User registration, login, and JWT-based authentication
- Password reset flow (forgot/reset) and authenticated password change
- Account lockout protection against brute-force attacks
- Full user CRUD with paginated listing and role-based access (admin/viewer)
- Single-use refresh token rotation with logout support
- Clean Architecture + DDD with 4-layer separation
- Environment-based YAML configuration
- Structured JSON logging with correlation IDs
- Rate limiting on auth endpoints (login, register, refresh, change-password, forgot/reset)
- Health check endpoints (liveness, readiness, combined health)
- Async PostgreSQL via SQLAlchemy 2.0 + Alembic migrations

[⬆️ Back to Top](#template-api-project)

## 🛠️ Technologies Used

- [Python 3.11](https://www.python.org/) — Core programming language
- [FastAPI](https://fastapi.tiangolo.com/) — Async web framework
- [Pydantic v2](https://docs.pydantic.dev/) — Data validation and serialization
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/) — Async ORM
- [Alembic](https://alembic.sqlalchemy.org/) — Database migrations
- [asyncpg](https://magicstack.github.io/asyncpg/) — Async PostgreSQL driver
- [PostgreSQL](https://www.postgresql.org/) — Relational database
- [bcrypt](https://pypi.org/project/bcrypt/) — Password hashing
- [PyJWT](https://pyjwt.readthedocs.io/) — JWT token handling
- [SlowAPI](https://slowapi.readthedocs.io/) — Rate limiting
- [Gunicorn](https://gunicorn.org/) + [Uvicorn](https://www.uvicorn.org/) — Production ASGI server
- [Docker](https://www.docker.com/) — Containerization

[⬆️ Back to Top](#template-api-project)

## 🚀 Getting Started

### ⚙️ Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- PostgreSQL (if not using Docker)

### 💾 Installation

```sh
# Clone the repositories
git clone https://github.com/your-username/template-api-python.git
cd template-api-python

```

[⬆️ Back to Top](#template-api-project)

### 📝 Configuration

The application uses environment-based YAML configuration files in `src/app/config/`. Available environments:

| Env | File | Use |
|-----|------|-----|
| `local` | `config_local.yml` | Local development (docs enabled) |
| `dev` | `config_dev.yml` | Shared development |
| `container` | `config_container.yml` | Docker deployment |
| `prod` | `config_prod.yml` | Production (docs disabled) |
| `test` | `config_test.yml` | Test environment |

Copy `.env.example` to `.env` and set your values:

```sh
cp .env.example .env
```

Key environment variables:
- `APP_ENV` — selects the config file (default: `dev`)
- `SECRET_KEY` — JWT signing secret
- `POSTGRES_PASSWORD` — database password

[⬆️ Back to Top](#template-api-project)

### Pip

- Create the pip environment:

  ```sh
   python -m venv venv
  ```

- Activate the pip environment:

  ```sh
   source venv/bin/activate
  ```

- Optional: Activate the pip environment (Windows)

   ```sh
    venv\Scripts\activate
  ```

- In case you need to update pip:

  ```sh
    pip install --upgrade pip
  ```

- Install the project's core dependencies:

  ```sh
   pip install -r requirements.txt
  ```

- Deactivate virtual environment:

  ```sh
  deactivate
  ```

### 🏃 Running the App

#### 🐳 Running with Docker

Ensure Docker and Docker Compose are installed on your system.

1. **Clean up existing containers and caches:**

   ```sh
   docker compose down --rmi all --volumes --remove-orphans
   ```

2. **Build and start the application:**

   ```sh
   docker compose up --build -d
   ```

3. **Access the app:**

   The app will be available at `http://localhost:8080`.  
   Swagger UI is available when running locally with `APP_ENV=local` or `APP_ENV=test` at `http://localhost:8000/docs`.  
   In Docker (`APP_ENV=container`), interactive docs are disabled for security.

   [Docker local run example](docs/running-app/docker-run.png)

---

#### 🖥️ Running with PyCharm

If you prefer running the app directly from the PyCharm IDE, follow these steps:

1. **Set up the Python interpreter:**

   - Navigate to PyCharm's settings (`File -> Settings -> Project -> Python Interpreter`).
   - Select the Python interpreter located at:  
     `your-repo/venv/bin/python`

2. **Configure the working directory:**

   - In your run configuration, set the **working directory** to:  
     `your-repo`

3. **Set up the module and script parameters:**

   - **Module:** `uvicorn`
   - **Script parameters:**  
     `src.main:app --reload`

4. **Run the application:**

   - Save the run configuration and start the app.

5. **Access the app:**

   The app will be available at:  
   `http://localhost:8000/docs`

   [PyCharm local run settings example](docs/running-app/pycharm-run-setup.png)

---

## 🗄️ Database Management

Alembic is pre-configured with async PostgreSQL support.

### Creating Migrations

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

## 🌱 Seed Users

A seed script at `scripts/seed_users.py` creates default test users on container startup. It runs automatically after migrations, before the app starts.

| Email | Password | Role |
|---|---|---|
| `admin@example.com` | `Admin123!` | admin |
| `viewer@example.com` | `Viewer123!` | viewer |

The script is **idempotent** — safe to run multiple times; existing users are skipped.

To run manually:

```bash
python scripts/seed_users.py
```

[⬆️ Back to Top](#template-api-project)

## 📡 API Endpoints

### Auth (`/api/v1`)

| Method | Path | Auth | Description |
|--------|------|:---:|-------------|
| `POST` | `/api/v1/register` | No | Register new user (auto-login, returns tokens) |
| `POST` | `/api/v1/login` | No | Login, returns access + refresh tokens + `expires_in` |
| `POST` | `/api/v1/refresh` | No* | Refresh access token (single-use rotation) |
| `POST` | `/api/v1/logout` | Yes | Revoke current access token |
| `POST` | `/api/v1/change-password` | Yes | Change password for authenticated user |
| `POST` | `/api/v1/auth/forgot-password` | No | Request password reset (generic response to prevent enumeration) |
| `POST` | `/api/v1/auth/reset-password` | No | Reset password with one-time token |

> *Refresh uses a refresh token instead of an access token. Rate limited: 10/15min.

### Users (`/api/v1/users`)

| Method | Path | Auth | Role | Description |
|--------|------|:---:|------|-------------|
| `GET` | `/api/v1/users/me` | Yes | any | Get current user profile |
| `GET` | `/api/v1/users/` | Yes | any | List users (paginated: `?skip=0&limit=20`) |
| `GET` | `/api/v1/users/{id}` | Yes | any | Get user by UUID |
| `POST` | `/api/v1/users/` | Yes | admin | Create user (any role) |
| `PUT` | `/api/v1/users/{id}` | Yes | admin | Update user (includes `isActive` for disable) |
| `DELETE` | `/api/v1/users/{id}` | Yes | admin | Delete user |

### Health

| Method | Path | Auth | Description |
|--------|------|:---:|-------------|
| `GET` | `/` | No | Welcome message |
| `GET` | `/health` | No | Application health |
| `GET` | `/health/live` | No | Liveness probe |
| `GET` | `/health/ready` | No | Readiness probe (checks DB) |

### Token Response Format

Login and register endpoints return:
```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "expiresIn": 900,
  "email": "user@example.com",
  "displayName": "John Doe",
  "loggedInAt": "2026-06-25T12:00:00Z",
  "role": "viewer",
  "user": {
    "email": "user@example.com",
    "displayName": "John Doe",
    "name": "John Doe",
    "role": "viewer"
  }
}
```

### Error Response Format

All errors include a machine-readable `error_code`:
```json
{
  "detail": "Invalid credentials",
  "error_code": "AUTH_INVALID_CREDENTIALS"
}
```

Error codes: `AUTH_INVALID_CREDENTIALS`, `AUTH_TOKEN_EXPIRED`, `AUTH_TOKEN_INVALID`, `AUTH_ACCOUNT_LOCKED`, `AUTH_INSUFFICIENT_PERMISSIONS`, `NOT_FOUND`, `NOT_FOUND_USER`, `CONFLICT_EMAIL_EXISTS`, `VALIDATION_ERROR`, `RATE_LIMIT_EXCEEDED`, `INTERNAL_ERROR`.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a pull request

---

[⬆️ Back to Top](#template-api-project)

_Built with ❤️ by [EndToEndLabCR](https://github.com/EndToEndLabCR)_
