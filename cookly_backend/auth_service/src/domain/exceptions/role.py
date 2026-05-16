from dataclasses import dataclass

from domain.common.exceptions.base import DomainError


@dataclass(eq=False)
class InvalidPermissionsError(DomainError):
    description: str

    @property
    def title(self) -> str:
        return f"Invalid Permissions: {self.description}"


@dataclass(eq=False)
class RoleNotFoundError(DomainError):

    @property
    def title(self) -> str:
        return "Roles not found (or not all found)"


# @dataclass(eq=False)
# class InvalidRoleNameError(DomainError):
#     @property
#     def title(self) -> str:
#         return ""
