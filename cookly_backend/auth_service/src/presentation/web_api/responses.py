from dataclasses import dataclass
from typing import Generic, TypeVar

from fastapi.responses import ORJSONResponse
from starlette import status

TResult = TypeVar("TResult")
TError = TypeVar("TError")


@dataclass(frozen=True)
class Response:
    pass


@dataclass(frozen=True)
class OkResponse(Response, Generic[TResult]):
    status: int = 200
    result: TResult | None = None


@dataclass(frozen=True)
class ErrorData(Generic[TError]):
    title: str
    data: TError | None = None

    def __post_init__(self):
        data = str(self.data)


@dataclass(frozen=True)
class ErrorResponse(Generic[TError]):
    status: int
    error: ErrorData[TError]


default_success = ORJSONResponse(
    {"status": "success"},
    status_code=status.HTTP_200_OK,
)
