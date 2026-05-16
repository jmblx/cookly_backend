from dataclasses import dataclass
from datetime import datetime
from typing import NewType, TypedDict
from uuid import UUID

from application.common.auth_server_token_types import (
    AuthServerAccessTokenPayload,
    BaseToken,
    RefreshTokenPayload,
)

ClientAccessToken = NewType("AuthServerAccessToken", BaseToken)
ClientRefreshToken = NewType("AuthServerRefreshToken", BaseToken)


@dataclass
class ClientRefreshTokenData:
    user_id: UUID
    jti: str
    created_at: datetime


class ClientRefreshTokenDataDict(TypedDict):
    user_id: str
    jti: str
    created_at: str


@dataclass
class ClientRefreshTokenWithData(ClientRefreshTokenData):
    token: ClientRefreshToken


class ClientAccessTokenPayload(AuthServerAccessTokenPayload):
    user_scopes: list[str]


class ClientRefreshTokenPayload(RefreshTokenPayload):
    client_id: int


class ClientTokens(TypedDict):
    access_token: ClientAccessToken
    refresh_token: ClientRefreshToken
