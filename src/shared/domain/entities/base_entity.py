from datetime import datetime
from dataclasses import field


class BaseEntity:
    __abstract__ = True

    created_at: str
    updated_at: str
