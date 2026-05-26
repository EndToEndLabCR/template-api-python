import re
from dataclasses import dataclass

import bcrypt


@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self):
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", self.value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", self.value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", self.value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/`~']", self.value):
            raise ValueError("Password must contain at least one special character")

    def hash(self) -> str:
        """Hash the password using bcrypt and return the hash as a string."""
        return bcrypt.hashpw(self.value.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def __str__(self) -> str:
        return self.value
