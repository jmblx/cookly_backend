from dataclasses import dataclass

from application.common.base_exceptions import ApplicationError
from domain.common.exceptions.base import DomainError


@dataclass(eq=False)
class InvalidTokenError(ApplicationError):
    @property
    def title(self) -> str:
        return "Invalid code fingerprint or user id mismatch"


@dataclass(eq=False)
class TokenExpiredError(ApplicationError):
    @property
    def title(self) -> str:
        return "Token expired."


@dataclass(eq=False)
class InvalidClientError(ApplicationError):
    @property
    def title(self) -> str:
        return "Invalid client."


@dataclass(eq=False)
class InvalidRedirectURLError(ApplicationError):
    redirect_url: str

    @property
    def title(self) -> str:
        return (
            f"{self.redirect_url} is not a valid redirect URL for your client."
        )


@dataclass(eq=False)
class InvalidCredentialsError(DomainError):
    @property
    def title(self) -> str:
        return "Invalid credentials."
