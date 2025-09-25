import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.config.app_config import AppConfig

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

@fastApiApp.get("/")
def read_root():
    return {"message": "Welcome to the API"}


@fastApiApp.get("/health")
def get_health_check():
    return "Ok"


