from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette import status

from application.auth_for_client.refresh_tokens_handler import (
    RefreshClientTokensHandler,
)
from application.auth_for_client.revoke_token_handler import (
    RevokeClientTokenHandler,
)
from application.common.client_token_types import ClientRefreshToken
from presentation.web_api.common.schemas import RefreshTokenRequest
from presentation.web_api.manage_tokens import set_client_tokens

client_token_manage_router = APIRouter(
    route_class=DishkaRoute, tags=["client-code-manage"], prefix="/client"
)


@client_token_manage_router.post("/refresh")
async def refresh_token(
    refresh_token: RefreshTokenRequest,  # noqa: for swagger
    handler: FromDishka[RefreshClientTokensHandler],
) -> ORJSONResponse:
    tokens = await handler.handle(refresh_token.refresh_token)
    response = ORJSONResponse(
        # {"access_token": access_token, "refresh_token": refresh_token},
        {"refresh_token": tokens["refresh_token"], "access_token": tokens["access_token"]},
        status_code=status.HTTP_200_OK,
    )
    # set_client_tokens(response, tokens)
    return response


@client_token_manage_router.post("/revoke")
async def revoke_token(
    refresh_token: RefreshTokenRequest,  # noqa: for swagger
    _refresh_token: FromDishka[ClientRefreshToken],
    handler: FromDishka[RevokeClientTokenHandler],
) -> ORJSONResponse:
    await handler.handle(_refresh_token)
    response = ORJSONResponse({"detail": "Tokens revoked successfully"})
    # response.delete_cookie("refresh_token")
    # response.delete_cookie("access_token")
    response.status_code = status.HTTP_200_OK
    return response
