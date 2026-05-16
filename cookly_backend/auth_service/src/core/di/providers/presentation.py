from typing import cast
from uuid import UUID

from dishka import Provider, Scope, provide
from fastapi import Request

from application.common.auth_server_token_types import (
    AuthServerAccessToken,
    AuthServerRefreshToken,
    AuthServerTokens,
    Fingerprint,
    NonActiveRefreshTokens,
)
from application.common.client_token_types import (
    ClientAccessToken,
    ClientRefreshToken,
)
from domain.entities.user.value_objects import UserID


class PresentationProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=Fingerprint)
    def provide_session(self, request: Request) -> Fingerprint:
        return Fingerprint(request.headers.get("X-Device-Fingerprint"))  # type: ignore

    @provide(scope=Scope.REQUEST, provides=AuthServerRefreshToken)
    def provide_auth_server_refresh_token(
        self, request: Request
    ) -> AuthServerRefreshToken:
        return AuthServerRefreshToken(request.cookies.get("refresh_token"))

    @provide(scope=Scope.REQUEST, provides=AuthServerAccessToken)
    def provide_auth_server_access_token(
        self, request: Request
    ) -> AuthServerAccessToken:
        return AuthServerRefreshToken(request.cookies.get("access_token"))
        # headers = {
        #     key.lower(): value for key, value in request.headers.items()
        # }
        #
        # auth_header = headers.get("authorization")
        #
        # return AuthServerAccessToken(auth_header.replace("Bearer ", ""))

    @provide(scope=Scope.REQUEST, provides=AuthServerTokens)
    def provide_auth_server_tokens(
        self,
        access_token: AuthServerAccessToken,
        refresh_token: AuthServerRefreshToken,
    ) -> AuthServerTokens:
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @provide(scope=Scope.REQUEST, provides=ClientAccessToken)
    def provide_client_access_token(
        self, request: Request
    ) -> ClientAccessToken:
        headers = {
            key.lower(): value for key, value in request.headers.items()
        }
        print(headers)
        auth_header = headers.get("authorization")
        if auth_header is None:
            return
        return ClientAccessToken(auth_header.replace("Bearer ", ""))

    @provide(scope=Scope.REQUEST, provides=ClientRefreshToken)
    async def provide_client_refresh_token(
        self, request: Request
    ) -> ClientRefreshToken:
        return ClientRefreshToken(request.scope.get("refresh_token"))

    @provide(scope=Scope.REQUEST, provides=NonActiveRefreshTokens)
    def provide_nonactive_refresh_tokens(
        self,
        request: Request,
    ) -> NonActiveRefreshTokens:
        return NonActiveRefreshTokens(
            {
                UserID(UUID(cookie.split(":")[1])): cast(
                    AuthServerRefreshToken, value
                )
                for cookie, value in request.cookies.items()
                if cookie.startswith("refresh_token:")
            }
        )
