from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.responses import Response

from application.auth_as.register_user_auth_server.confirm_registration_handler import CompleteRegisterUserHandler, \
    CompleteRegisterUserCommand
from application.auth_as.register_user_auth_server.init_registration_hander import (
    InitRegisterUserCommand,
    InitRegisterUserHandler,
)
from domain.exceptions.auth import (
    InvalidClientError,
    InvalidRedirectURLError,
)
from domain.exceptions.user import UserAlreadyExistsError
from presentation.web_api.manage_tokens import set_auth_server_tokens
from presentation.web_api.responses import ErrorResponse

reg_router = APIRouter(route_class=DishkaRoute, tags=["reg"])


@reg_router.post(
    "/register",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "user created",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse[
                InvalidRedirectURLError | InvalidClientError
            ],
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse[UserAlreadyExistsError],
        },
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def init_registration(
    handler: FromDishka[InitRegisterUserHandler],
    command: InitRegisterUserCommand,
) -> Response:
    await handler.handle(command)
    response = Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
    return response


@reg_router.post(
    "/complete-register",
    responses={
        status.HTTP_201_CREATED: {
            "description": "user created",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse[
                InvalidRedirectURLError | InvalidClientError
            ],
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse[UserAlreadyExistsError],
        },
    },
    status_code=status.HTTP_201_CREATED,
)
async def registration(
    handler: FromDishka[CompleteRegisterUserHandler],
    command: CompleteRegisterUserCommand,
) -> ORJSONResponse:
    complete_register_handler_response = await handler.handle(command)
    response = ORJSONResponse(
        {"id": complete_register_handler_response["user_id"]},
        status_code=status.HTTP_201_CREATED,
    )
    set_auth_server_tokens(response, complete_register_handler_response)
    return response
