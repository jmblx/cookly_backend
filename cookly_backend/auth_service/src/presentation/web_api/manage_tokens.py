import logging
from typing import cast
from uuid import UUID

from fastapi import Request
from fastapi.responses import ORJSONResponse

from application.common.auth_server_token_types import (
    AuthServerAccessToken,
    AuthServerRefreshToken,
    AuthServerTokens,
)
from application.common.client_token_types import ClientTokens
from domain.exceptions.auth import InvalidTokenError

logger = logging.getLogger(__name__)


base_refresh_token_settings = {
    "httponly": True,
    "secure": False,
    "max_age": 60 * 60 * 24 * 30,
    "expires": 60 * 60 * 24 * 30,
    "samesite": "strict",
}

base_access_token_settings = {
    "httponly": True,
    "secure": False,
    "max_age": 60 * 60 * 24 * 30,
    "expires": 60 * 60 * 24 * 30,
    "samesite": "strict",
}


def set_auth_server_tokens(response: ORJSONResponse, tokens: AuthServerTokens):
    response.set_cookie(
        **base_refresh_token_settings,
        key="refresh_token",
        value=tokens.get("refresh_token"),
    )
    response.set_cookie(
        **base_access_token_settings,
        key="access_token",
        value=tokens.get("access_token"),
    )


def change_active_account(
    response: ORJSONResponse,
    prev_account_id: str,
    prev_account_tokens: AuthServerTokens,
    new_tokens: AuthServerTokens,
    new_active_account_id: str,
):
    response.set_cookie(
        **base_refresh_token_settings,
        key=f"refresh_token:{prev_account_id}",
        value=prev_account_tokens.get("refresh_token"),
    )
    response.set_cookie(
        **base_access_token_settings,
        key=f"access_token:{prev_account_id}",
        value=prev_account_tokens.get("access_token"),
    )
    # response.delete_cookie(f"refresh_token:{new_active_account_id}")
    # response.delete_cookie(f"access_token:{new_active_account_id}")
    set_auth_server_tokens(response, new_tokens)


def get_tokens_by_user_id(
    request: Request, new_active_user_id: str
) -> AuthServerTokens | None:
    access_token = request.cookies.get(f"access_token:{new_active_user_id}")
    refresh_token = request.cookies.get(f"refresh_token:{new_active_user_id}")
    if not access_token or not refresh_token:
        return None
    return {
        "access_token": cast(AuthServerAccessToken, access_token),
        "refresh_token": cast(AuthServerRefreshToken, refresh_token),
    }


def activate_account(
    response: ORJSONResponse,
    new_active_account_id: str,
    new_tokens: AuthServerTokens,
):
    response.set_cookie(
        **base_refresh_token_settings,
        key="refresh_token",
        value=new_tokens.get("refresh_token"),
    )
    response.set_cookie(
        **base_access_token_settings,
        key="access_token",
        value=new_tokens.get("access_token"),
    )
    response.set_cookie(
        **base_refresh_token_settings,
        key=f"refresh_token:{new_active_account_id}",
        value=new_tokens.get("refresh_token"),
    )
    response.set_cookie(
        **base_access_token_settings,
        key=f"access_token:{new_active_account_id}",
        value=new_tokens.get("access_token"),
    )


def deactivate_account_tokens(
    response: ORJSONResponse, prev_account_id: str, prev_account_tokens
):
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    response.set_cookie(
        **base_refresh_token_settings,
        key=f"refresh_token:{prev_account_id}",
        value=prev_account_tokens.get("refresh_token"),
    )
    response.set_cookie(
        **base_access_token_settings,
        key=f"access_token:{prev_account_id}",
        value=prev_account_tokens.get("access_token"),
    )


def set_client_tokens(response: ORJSONResponse, tokens: ClientTokens):
    response.set_cookie(
        **base_refresh_token_settings,
        key="client_refresh_token",
        value=tokens.get("refresh_token"),
    )
    response.set_cookie(
        **base_access_token_settings,
        key="client_access_token",
        value=tokens.get("access_token"),
    )
