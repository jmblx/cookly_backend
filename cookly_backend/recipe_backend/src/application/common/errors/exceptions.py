from dataclasses import dataclass, field

from application.common.errors.base import ApplicationError


@dataclass(eq=False)
class PermissionDeniedError(ApplicationError):
    reason: str | None = field(default="")

    @property
    def title(self) -> str:
        return f"Permission denied: {self.reason}" if self.reason else "Permission denied"


@dataclass(eq=False)
class NotFoundError(ApplicationError):
    description: str | None = None

    @property
    def title(self) -> str:
        return f"Not found: {self.description}" if self.description else "Not found"


@dataclass
class InfrastructureError(ApplicationError):
    @property
    def title(self) -> str:
        return "S3 storage error"
