import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.app.config.app_config import AppConfig

from src.app.features.presentation.web.routes.user_routes import router as user_router
from src.app.features.application.exceptions.user_exception import UserDoesNotExistException

ENV = os.getenv("APP_ENV", "local")

config = AppConfig.instance()
app_name = config.get_config("app.name")
app_version = config.get_config("app.version")

fastApiApp = FastAPI(title=app_name, version=app_version)

if ENV not in ("local", "container"):
    fastApiApp.docs_url = None
    fastApiApp.redoc_url = None
    fastApiApp.openapi_url = None

# --- CORS Origins from config ---
origins = [
    "http://localhost"
]

fastApiApp.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Exception Handlers
@fastApiApp.exception_handler(UserDoesNotExistException)
async def user_not_found_exception_handler(request: Request, exc: UserDoesNotExistException):
    """Handle UserDoesNotExistException and return 404 response."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )


@fastApiApp.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """Handle ValueError (e.g., invalid UUID format) and return 400 response."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@fastApiApp.get("/")
def read_root():
    return {"message": "Welcome to the API"}


@fastApiApp.get("/health")
def get_health_check():
    return "Ok"

# TODO validate best practices for endpoint naming conventions
fastApiApp.include_router(user_router, prefix="/v1/user", tags=["Users"])


