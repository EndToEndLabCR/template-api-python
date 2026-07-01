"""
Standardized error codes for API error responses.

All error responses include an `error_code` field alongside `detail`
so the frontend can handle errors programmatically.
"""


class ErrorCode:
    """Machine-readable error codes for API error responses."""

    # Auth errors
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_TOKEN_REVOKED = "AUTH_TOKEN_REVOKED"
    AUTH_ACCOUNT_LOCKED = "AUTH_ACCOUNT_LOCKED"
    AUTH_ACCOUNT_INACTIVE = "AUTH_ACCOUNT_INACTIVE"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"

    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    NOT_FOUND_USER = "NOT_FOUND_USER"
    CONFLICT_EMAIL_EXISTS = "CONFLICT_EMAIL_EXISTS"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Server errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
