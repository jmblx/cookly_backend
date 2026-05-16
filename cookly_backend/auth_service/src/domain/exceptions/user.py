from dataclasses import dataclass

from domain.common.exceptions.base import DomainError
from domain.entities.user.value_objects import Email


@dataclass(eq=False)
class UserNotFoundByIdError(DomainError):
    user_id: str

    @property
    def title(self) -> str:
        return f"User with id {self.user_id} not found."


@dataclass(eq=False)
class UserAlreadyExistsError(DomainError):
    email: str

    @property
    def title(self) -> str:
        return f"{self.email} is already registered."


@dataclass(eq=False)
class UserNotFoundByEmailError(DomainError):
    email: str

    @property
    def title(self) -> str:
        return f"{self.email} doesn't exists."


@dataclass(eq=False)
class UnauthenticatedUserError(DomainError):
    @property
    def title(self) -> str:
        return "Unauthenticated user."


@dataclass(eq=False)
class ThirdPartyUserNotRegisteredError(DomainError):
    email: Email

    @property
    def title(self) -> str:
        return f"Third party user with email {self.email} not registered."
