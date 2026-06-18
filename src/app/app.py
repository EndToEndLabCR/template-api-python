import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.config.app_config import AppConfig

from app.features.user.presentation.web.routes.user_routes import router as user_router
from app.features.user.presentation.web import router as auth_router
from app.features.user.presentation.web.routes.password_routes import router as password_router

ENV = os.getenv("APP_ENV", "local")

config = AppConfig.instance()
app_name = config.get_config("app.name")
app_version = config.get_config("app.version")

fastapi_app = FastAPI(title=app_name, version=app_version)

if ENV not in ("local", "container"):
    fastapi_app.docs_url = None
    fastapi_app.redoc_url = None
    fastapi_app.openapi_url = None

# --- CORS Origins from config ---
origins = [
    "http://localhost:5173",
    "http://localhost:*",
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@fastapi_app.get("/")
def read_root():
    return {"message": "Welcome to the API"}


@fastapi_app.get("/health")
def get_health_check():
    return "Ok"

# TODO validate best practices for endpoint naming conventions
fastapi_app.include_router(user_router, prefix="/v1/user", tags=["Users"])
fastapi_app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
fastapi_app.include_router(password_router, prefix="/api/v1", tags=["Password"])
