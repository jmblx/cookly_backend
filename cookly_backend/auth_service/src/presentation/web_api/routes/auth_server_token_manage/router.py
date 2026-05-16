from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_200_OK

from application.auth_as.invalidate_other_tokens_handler import (
    InvalidateOtherTokensCommand,
    InvalidateOtherTokensHandler,
)
from application.auth_as.refresh_tokens_auth_server_handler import (
    RefreshTokensHandler,
)
from application.auth_as.revoke_token_handler import (
    RevokeTokenHandler,
)
from application.common.auth_server_token_types import (
    AuthServerRefreshToken,
    Fingerprint,
)
from application.common.id_provider import UserIdentityProvider
from presentation.web_api.manage_tokens import set_auth_server_tokens

token_manage_router = APIRouter(
    route_class=DishkaRoute,
    tags=["auth-server-code-manage"],
    prefix="/auth-service",
)


@token_manage_router.post("/refresh")
async def refresh_token(
    handler: FromDishka[RefreshTokensHandler],
) -> ORJSONResponse:
    tokens = await handler.handle()
    response = ORJSONResponse(
        # {"access_token": access_token, "refresh_token": refresh_token},
        {"status": "success"},
        status_code=status.HTTP_200_OK,
    )
    set_auth_server_tokens(response, tokens)
    return response


@token_manage_router.post("/revoke")
async def revoke_token(
    refresh_token: FromDishka[AuthServerRefreshToken],
    idp: FromDishka[UserIdentityProvider],
    handler: FromDishka[RevokeTokenHandler],
) -> ORJSONResponse:
    await handler.handle(refresh_token)
    user_id = await idp.get_unvalidated_user_id()
    response = ORJSONResponse({"detail": "Tokens revoked successfully"})
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    response.delete_cookie(f"refresh_token:{user_id.value}")
    response.delete_cookie(f"access_token:{user_id.value}")
    response.status_code = HTTP_200_OK
    return response


@token_manage_router.post("/invalidate-others")
async def invalidate_others(
    handler: FromDishka[InvalidateOtherTokensHandler],
    refresh_token: FromDishka[AuthServerRefreshToken],
    fingerprint: FromDishka[Fingerprint],
    response: Response,
) -> ORJSONResponse:
    command = InvalidateOtherTokensCommand(
        refresh_token=refresh_token, fingerprint=fingerprint
    )
    await handler.handle(command)
    response.status_code = status.HTTP_204_NO_CONTENT
