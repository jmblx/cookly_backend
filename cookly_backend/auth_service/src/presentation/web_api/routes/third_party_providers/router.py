from dishka import FromDishka, AsyncContainer
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from starlette import status

from application.common.auth_server_token_types import AuthServerTokens
from application.third_party_auth.yandex.login_handler import (
    YandexLoginCommand,
    YandexLoginHandler,
)
from application.third_party_auth.yandex.register_handler import (
    YandexRegisterCommand,
    YandexRegisterHandler,
)
from domain.exceptions.user import UserAlreadyExistsError, ThirdPartyUserNotRegisteredError
from presentation.web_api.manage_tokens import (
    change_active_account,
    set_auth_server_tokens,
)

third_party_router = APIRouter(
    route_class=DishkaRoute, tags=["third-party-providers"]
)


@third_party_router.post("/login/yandex")
async def login_with_yandex(
    handler: FromDishka[YandexLoginHandler],
    command: YandexLoginCommand,
    prev_account_tokens: FromDishka[AuthServerTokens],
    container: FromDishka[AsyncContainer],
) -> ORJSONResponse:
    try:
        # Пытаемся залогиниться
        new_jwt_tokens, prev_active_account_id, new_active_user_id = (
            await handler.handle(command)
        )
        response = ORJSONResponse(
            {"status": "success"},
            status_code=status.HTTP_200_OK,
        )
        if prev_active_account_id:
            change_active_account(
                response,
                str(prev_active_account_id.value),
                prev_account_tokens,
                new_jwt_tokens,
                str(new_active_user_id.value),
            )
        else:
            set_auth_server_tokens(response, new_jwt_tokens)
        return response

    except ThirdPartyUserNotRegisteredError as e:
        register_handler = await container.get(YandexRegisterHandler)
        register_command = YandexRegisterCommand(
            yandex_token=command.yandex_token,
        )

        register_handler_response = await register_handler.handle(register_command)
        response = ORJSONResponse(
            {"id": register_handler_response["user_id"]},
            status_code=status.HTTP_201_CREATED,
        )
        set_auth_server_tokens(response, register_handler_response)
        return response


@third_party_router.post("/register/yandex")
async def register_with_yandex(
    handler: FromDishka[YandexRegisterHandler],
    command: YandexRegisterCommand,
    prev_account_tokens: FromDishka[AuthServerTokens],
    container: FromDishka[AsyncContainer],
):
    try:
        register_handler_response = await handler.handle(command)
        response = ORJSONResponse(
            {"id": register_handler_response["user_id"]},
            status_code=status.HTTP_201_CREATED,
        )
        set_auth_server_tokens(response, register_handler_response)
        return response
    except UserAlreadyExistsError as e:
        login_handler = await container.get(YandexLoginHandler)

        login_command = YandexLoginCommand(
            yandex_token=command.yandex_token,  # Или другие поля, которые нужны для логина
        )

        new_jwt_tokens, prev_active_account_id, new_active_user_id = (
            await login_handler.handle(login_command)
        )

        response = ORJSONResponse(
            {"status": "success"},
            status_code=status.HTTP_200_OK,
        )

        if prev_active_account_id:
            change_active_account(
                response,
                str(prev_active_account_id.value),
                prev_account_tokens,
                new_jwt_tokens,
                str(new_active_user_id.value),
            )
        else:
            set_auth_server_tokens(response, new_jwt_tokens)
        return response
