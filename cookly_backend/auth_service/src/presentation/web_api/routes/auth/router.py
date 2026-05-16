import logging

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse
from starlette import status

from application.auth_as.get_available_accounts_query import (
    GetAvailableAccountsHandler,
    GetAvailableAccountsQuery,
    GetAvailableAccountsResponse,
)
from application.auth_as.login_user_auth_server import (
    AuthenticateUserCommand,
    LoginUserHandler,
)
from application.auth_for_client.code_to_token_handler import (
    CodeToTokenCommand,
    CodeToTokenHandler,
)
from application.auth_for_client.get_me_page_data_handler import (
    GetMeDataCommand,
    GetMeDataHandler,
    MeData,
)
from application.common.auth_server_token_types import (
    AuthServerTokens,
    NonActiveRefreshTokens,
)
from application.common.id_provider import UserIdentityProvider
from domain.exceptions.user import UnauthenticatedUserError
from presentation.web_api.manage_tokens import (
    activate_account,
    change_active_account,
    deactivate_account_tokens,
    get_tokens_by_user_id,
    set_auth_server_tokens,
    set_client_tokens, base_refresh_token_settings, base_access_token_settings,
)
from presentation.web_api.routes.auth.models import (
    GetMePageDataSchema,
    NewActiveUserSchema,
)

auth_router = APIRouter(route_class=DishkaRoute, tags=["auth"])
# jinja_loader = PackageLoader("presentation.web_api.registration")
# templates = Jinja2Templates(directory="templates", loader=jinja_loader)


logger = logging.getLogger(__name__)


@auth_router.post("/login")
async def login(
    command: AuthenticateUserCommand,
    handler: FromDishka[LoginUserHandler],
    prev_account_tokens: FromDishka[AuthServerTokens],
) -> ORJSONResponse:
    new_jwt_tokens, prev_active_account_id, new_active_user_id = (
        await handler.handle(command)
    )
    response = ORJSONResponse(
        {"status": "success"},
        status_code=status.HTTP_200_OK,
    )
    if prev_active_account_id and prev_active_account_id != new_active_user_id:
        change_active_account(
            response,
            str(prev_active_account_id.value),
            prev_account_tokens,
            new_jwt_tokens,
            str(new_active_user_id.value),
        )
    else:
        set_auth_server_tokens(response, new_jwt_tokens)
    response.set_cookie(
        **base_refresh_token_settings,
        key=f"refresh_token:{new_active_user_id.value}",
        value=new_jwt_tokens.get("refresh_token"),
    )
    response.set_cookie(
        **base_access_token_settings,
        key=f"access_token:{new_active_user_id.value}",
        value=new_jwt_tokens.get("access_token"),
    )

    return response


@auth_router.post("/code-to-token")
async def code_to_token(
    handler: FromDishka[CodeToTokenHandler],
    command: CodeToTokenCommand,
) -> ORJSONResponse:
    response_data = await handler.handle(command)
    tokens = {
        "access_token": response_data.get("access_token", None),
        "refresh_token": response_data.get("refresh_token", None),
    }

    response = ORJSONResponse(
        {"refresh_token": tokens["refresh_token"], "access_token": tokens["access_token"]},
        status_code=status.HTTP_200_OK,
    )

    return response


@auth_router.post("/auth-to-client")
async def auth_to_client(
    handler: FromDishka[GetMeDataHandler], command: GetMePageDataSchema
) -> MeData:
    command_data = GetMeDataCommand(
        ref_id=command.ref_id,
        redirect_url=str(command.redirect_url),
        code_verifier=command.code_verifier,
        code_challenge_method=command.code_challenge_method,
    )
    return await handler.handle(command_data)


@auth_router.post("/switch-account")
async def switch_account(
    idp: FromDishka[UserIdentityProvider],
    active_account_tokens: FromDishka[AuthServerTokens],
    new_active_user: NewActiveUserSchema,
    request: Request,
) -> ORJSONResponse:
    active_user_id = await idp.get_current_user_id()
    response = ORJSONResponse(
        content={"status": "success"}, status_code=status.HTTP_200_OK
    )
    if not active_user_id:
        raise UnauthenticatedUserError()
    if new_active_user.new_active_user_id == active_user_id:
        return response

    change_active_account(
        response,
        str(active_user_id.value),
        active_account_tokens,
        get_tokens_by_user_id(
            request, str(new_active_user.new_active_user_id)
        ),
        str(new_active_user.new_active_user_id),
    )
    return response


@auth_router.get("/available-accounts")
async def get_available_accounts(
    handler: FromDishka[GetAvailableAccountsHandler],
    non_active_tokens: FromDishka[NonActiveRefreshTokens],
) -> GetAvailableAccountsResponse:
    return await handler.handle(GetAvailableAccountsQuery(non_active_tokens))


@auth_router.post("/deactivate-current-account")
async def deactivate_account(
    idp: FromDishka[UserIdentityProvider],
    prev_account_tokens: FromDishka[AuthServerTokens],
):
    response = ORJSONResponse(
        content={"status": "success"}, status_code=status.HTTP_200_OK
    )
    current_user_id = await idp.get_current_user_id()

    if current_user_id:
        deactivate_account_tokens(
            response,
            str(current_user_id.value),
            prev_account_tokens,
        )

    return response


@auth_router.post("/activate-account")
async def activate_account_tokens(
    new_active_user: NewActiveUserSchema,
    request: Request,
) -> ORJSONResponse:
    response = ORJSONResponse(
        content={"status": "success"}, status_code=status.HTTP_200_OK
    )
    new_active_user_tokens = get_tokens_by_user_id(
        request, str(new_active_user.new_active_user_id)
    )
    if not new_active_user_tokens:
        raise UnauthenticatedUserError()
    activate_account(
        response,
        str(new_active_user.new_active_user_id),
        new_active_user_tokens,
    )
    return response


# @auth_router.get("/pages/login")
# async def login_page(  # type: ignore
#         data: Annotated[UserAuthRequest, Param()],
#         client_service: FromDishka[ClientService],
#         request: Request,
# ):
#     client = await client_service.get_validated_client(data)
#     return templates.TemplateResponse(
#         "login.html",
#         convert_request_to_render(client, data, request),
#     )
