"""
Router registration for FastAPI application.
Centralizes API route registration with consistent prefixing and tagging.
"""

from fastapi import FastAPI

from src.app.features.auth.presentation.auth_routes import router as auth_router
from src.app.features.auth.presentation.password_routes import router as password_router
from src.app.features.user.presentation.web.routes.user_routes import (
    router as user_router,
)


def register_routers(app: FastAPI) -> None:
    """Register all feature routers with the FastAPI application.

    Auth routes:   /api/v1 (login, register, refresh)
    Password:      /api/v1/auth (forgot/reset password)
    User routes:   /api/v1/users (CRUD — GET/DELETE by ID)
    """
    app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
    app.include_router(password_router, prefix="/api/v1", tags=["Password"])
    app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
