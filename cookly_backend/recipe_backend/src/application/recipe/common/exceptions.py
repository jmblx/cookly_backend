from dataclasses import dataclass, field

from application.common.errors.base import ApplicationError


@dataclass
class InvalidRecipeError(ApplicationError):
    reason: str | None = field(default="")

    @property
    def title(self) -> str:
        return "Invalid recipe: %s".format() if self.reason else "Invalid recipe"


@dataclass
class RecipeNotFoundError(ApplicationError):
    reason: str | None = field(default="")

    @property
    def title(self) -> str:
        return "Recipe not found: %s".format() if self.reason else "Recipe not found"


@dataclass
class RecipeStepNotFoundError(ApplicationError):
    reason: str | None = field(default="")

    @property
    def title(self) -> str:
        return "Recipe step not found: %s".format() if self.reason else "Recipe step not found"


@dataclass
class RecipeAlreadyPublishedError(ApplicationError):
    @property
    def title(self) -> str:
        return "Recipe already published"


@dataclass
class SessionIsNotActiveError(ApplicationError):

    @property
    def title(self) -> str:
        return "Session is currently not active"


@dataclass
class InvalidRecipeRateError(ApplicationError):
    @property
    def title(self) -> str:
        return "Invalid recipe rate. Must be a positive number between 1 and 5"


@dataclass
class AuthorRecipeRateError(ApplicationError):
    @property
    def title(self) -> str:
        return "Author cannot rate their own recipe"


@dataclass
class InvalidImageError(ApplicationError):
    @property
    def title(self) -> str:
        return "Invalid image format. Must be a valid image file"
