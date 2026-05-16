from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, field_serializer

from presentation.web_api.tz_context import current_tz

TError = TypeVar("TError")


@dataclass(frozen=True)
class Response:
    pass


@dataclass(frozen=True)
class ErrorData(Generic[TError]):
    title: str
    data: TError | None = None


@dataclass(frozen=True)
class ErrorResponse(Response, Generic[TError]):
    status: int
    error: ErrorData[TError]


class BaseResponse(BaseModel):
    @field_serializer("*", when_used="json")
    def serialize_datetime(self, value, info):
        if isinstance(value, datetime):
            tz = current_tz.get()
            if value.tzinfo is None:
                return value
            return value.astimezone(tz)
        return value
