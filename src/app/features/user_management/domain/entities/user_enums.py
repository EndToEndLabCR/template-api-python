from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    STAFF = "staff"


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
