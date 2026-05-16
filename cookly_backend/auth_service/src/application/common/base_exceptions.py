from domain.common.exceptions.base import AppError


class ApplicationError(AppError):
    """Base Application Exception."""

    @property
    def title(self) -> str:
        return "An application error occurred"


class UnexpectedError(ApplicationError):
    pass


class RepoError(UnexpectedError):
    pass
