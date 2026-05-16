import logging
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from functools import partial

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from application.common.exceptions import FingerprintMismatchException
from core.exceptions.user_password.exceptions import InvalidResetPasswordCode
from domain.common.exceptions.base import AppError
from domain.exceptions.auth import (
    InvalidClientError,
    InvalidCredentialsError,
    InvalidRedirectURLError,
    InvalidTokenError,
)
from domain.exceptions.user import (
    UnauthenticatedUserError,
    UserAlreadyExistsError,
    UserNotFoundByIdError,
)
from infrastructure.external_services.storage.exceptions import InvalidImageError
from presentation.web_api.config import TRACING
from presentation.web_api.middlewares.metrics import APP_NAME
from presentation.web_api.middlewares.metrics.labels import EXCEPTIONS
from presentation.web_api.responses import ErrorData, ErrorResponse

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppError, error_handler(500))
    app.add_exception_handler(
        InvalidRedirectURLError, error_handler(status.HTTP_400_BAD_REQUEST)
    )
    app.add_exception_handler(
        FingerprintMismatchException,
        error_handler(status.HTTP_401_UNAUTHORIZED),
    )
    app.add_exception_handler(
        InvalidClientError, error_handler(status.HTTP_400_BAD_REQUEST)
    )
    app.add_exception_handler(
        UserAlreadyExistsError, error_handler(status.HTTP_409_CONFLICT)
    )
    app.add_exception_handler(
        UserNotFoundByIdError, error_handler(status.HTTP_409_CONFLICT)
    )
    app.add_exception_handler(
        UnauthenticatedUserError, error_handler(status.HTTP_401_UNAUTHORIZED)
    )
    app.add_exception_handler(
        InvalidResetPasswordCode, error_handler(status.HTTP_400_BAD_REQUEST)
    )
    app.add_exception_handler(
        InvalidCredentialsError, error_handler(status.HTTP_403_FORBIDDEN)
    )
    app.add_exception_handler(
        InvalidTokenError, error_handler(status.HTTP_401_UNAUTHORIZED)
    )
    app.add_exception_handler(InvalidImageError, error_handler(status.HTTP_400_BAD_REQUEST))
    app.add_exception_handler(Exception, unknown_exception_handler)


def error_handler(
    status_code: int,
) -> Callable[..., Awaitable[ORJSONResponse]]:
    return partial(app_error_handler, status_code=status_code)


async def app_error_handler(
    request: Request, err: AppError, status_code: int
) -> ORJSONResponse:
    method = request.method
    path = request.url.path

    logger.error("Handle error", exc_info=err, extra={"error": err})

    if TRACING:
        EXCEPTIONS.labels(
            method=method,
            path=path,
            exception_type=type(err).__name__,
            app_name=APP_NAME,
        ).inc()

    return handle_error(
        request=request,
        err=err,
        err_data=ErrorData(title=err.title, data=err.title),
        status=err.status,
        status_code=status_code,
    )


async def unknown_exception_handler(
    request: Request, err: Exception
) -> ORJSONResponse:
    method = request.method
    path = request.url.path

    logger.error("Handle error", exc_info=err, extra={"error": err})
    logger.exception(
        "Unknown error occurred", exc_info=err, extra={"error": err}
    )

    if TRACING:
        EXCEPTIONS.labels(
            method=method,
            path=path,
            exception_type=type(err).__name__,
            app_name=APP_NAME,
        ).inc()

    return ORJSONResponse(
        ErrorResponse(
            error=ErrorData(data=str(err), title="Unknown error"),
            status=HTTP_500_INTERNAL_SERVER_ERROR,
        ),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def handle_error(
    request: Request,
    err: Exception,
    err_data: ErrorData,
    status: int,
    status_code: int,
) -> ORJSONResponse:
    response = ErrorResponse(status=status_code, error=err_data)
    return ORJSONResponse(asdict(response), status_code=response.status)
