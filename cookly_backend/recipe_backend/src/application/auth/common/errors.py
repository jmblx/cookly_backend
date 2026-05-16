from dataclasses import dataclass

from application.common.errors.base import ApplicationError


@dataclass(eq=False)
class EmailAlreadyRegisteredError(ApplicationError):
    @property
    def title(self) -> str:
        return "Email Already Registered"


@dataclass(eq=False)
class UserNotFoundError(ApplicationError):
    by: str

    @property
    def title(self) -> str:
        return "User not found by %s".format()


@dataclass(eq=False)
class PwdMismatchError(ApplicationError):
    @property
    def title(self) -> str:
        return "Login password mismatch"


@dataclass(eq=False)
class UnauthorizedError(ApplicationError):
    @property
    def title(self) -> str:
        return "Unauthorized"
