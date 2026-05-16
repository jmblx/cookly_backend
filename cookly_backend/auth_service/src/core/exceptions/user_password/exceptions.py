from dataclasses import dataclass

from application.common.base_exceptions import ApplicationError


@dataclass(eq=False)
class InvalidResetPasswordCode(ApplicationError):
    @property
    def title(self) -> str:
        return "Invalid reset password code"


@dataclass(eq=False)
class InvalidResetPasswordToken(ApplicationError):
    @property
    def title(self) -> str:
        return "Invalid reset password token"
