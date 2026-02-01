"""
Exception handlers for the presentation layer.

This module contains exception handlers for API routes, converting
application-level exceptions to appropriate HTTP responses.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.app.features.application.exceptions.user_exception import UserDoesNotExistException


async def user_not_found_exception_handler(request: Request, exc: UserDoesNotExistException):
    """
    Handle UserDoesNotExistException and return 404 response.
    
    Args:
        request (Request): The incoming request.
        exc (UserDoesNotExistException): The exception instance.
        
    Returns:
        JSONResponse: A 404 response with error details.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )


async def value_error_exception_handler(request: Request, exc: ValueError):
    """
    Handle ValueError (e.g., invalid UUID format) and return 400 response.
    
    Args:
        request (Request): The incoming request.
        exc (ValueError): The exception instance.
        
    Returns:
        JSONResponse: A 400 response with error details.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all presentation layer exception handlers with the FastAPI app.
    
    This function should be called when setting up the application to register
    exception handlers for the presentation layer. Keeping exception handlers
    in the presentation layer (rather than app.py) maintains better separation
    of concerns and keeps app.py clean as more features are added.
    
    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.add_exception_handler(UserDoesNotExistException, user_not_found_exception_handler)
    app.add_exception_handler(ValueError, value_error_exception_handler)
