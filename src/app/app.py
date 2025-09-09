import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.config.app_config import AppConfig
from src.app.features.user_management.infrastructure.web.routes.user_routes import router as user_router

ENV = os.getenv("APP_ENV", "local")

config = AppConfig.instance()
app_name = config.get_config("app.name")
app_version = config.get_config("app.version")

fastApiApp = FastAPI(title=app_name, root_path="/api", version=app_version)

if ENV not in ("local", "container"):
    fastApiApp.docs_url = None
    fastApiApp.redoc_url = None
    fastApiApp.openapi_url = None

# --- CORS Origins from config ---
origins = [
    "http://localhost",  # Add your React app's URL here
    "http://clinic-alb-1726800379.us-east-1.elb.amazonaws.com"
]

fastApiApp.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@fastApiApp.get("/health")
def get_health_check():
    return "Ok"


fastApiApp.include_router(user_router)
