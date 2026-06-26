"""
User feature dependencies — re-exports use case factories from composition root.
No service layer — use cases are injected directly into routes.
"""

from src.app.composition import (
    get_delete_user_use_case,
    get_user_by_id_use_case,
)

__all__ = [
    "get_user_by_id_use_case",
    "get_delete_user_use_case",
]
