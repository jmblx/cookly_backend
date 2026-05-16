from dataclasses import dataclass

from application.common.base_exceptions import ApplicationError


@dataclass
class InvalidImageError(ApplicationError):
    @property
    def title(self) -> str:
        return "Invalid image format. Must be a valid image file"
