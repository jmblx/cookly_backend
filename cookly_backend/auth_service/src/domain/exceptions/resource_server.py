from dataclasses import dataclass

from domain.common.exceptions.base import DomainError


@dataclass(eq=False)
class ResourceServerNotFoundError(DomainError):

    @property
    def title(self) -> str:
        return "ResourceServer not found"
