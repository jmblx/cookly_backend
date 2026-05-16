import re
from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.exceptions.user_vo import (
    InvalidEmailError,
)


@dataclass(frozen=True)
class RawPassword:
    value: str

    def _validate(self) -> bool:
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$'
        return bool(re.match(pattern, self.value))


@dataclass(frozen=True)
class HashedPassword:
    value: str

    # @staticmethod
    # def create(password: str, hash_service) -> "HashedPassword":
    #     hashed = hash_service.hash_password(password)
    #     return HashedPassword(hashed)


@dataclass(frozen=True)
class UserID:
    value: UUID

    @staticmethod
    def generate():
        return UserID(uuid4())


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self.is_valid_email(self.value):
            raise InvalidEmailError(f"Invalid email address: {self.value}")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))
