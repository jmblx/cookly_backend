from dataclasses import dataclass
from datetime import datetime
from typing import NewType, TypedDict
from uuid import UUID

from domain.entities.user.value_objects import UserID

BaseToken = NewType("BaseToken", str)
Fingerprint = NewType("Fingerprint", str)
AuthServerRefreshToken = NewType("AuthServerRefreshToken", BaseToken)
AuthServerAccessToken = NewType("AuthServerAccessToken", BaseToken)
NonActiveRefreshTokens = NewType(
    "NonActiveRefreshTokens", dict[UserID, AuthServerRefreshToken]
)


class AuthServerAccessTokenPayload(TypedDict, total=False):
    """Типизированный словарь для представления данных в payload JWT."""

    sub: UserID
    exp: datetime
    iat: datetime
    jti: UUID


class AccessTokenPayload(TypedDict):
    sub: str
    email: str
    scopes: dict[str, str]


class JwtToken(TypedDict):
    token: BaseToken
    created_at: datetime
    expires_at: datetime


@dataclass
class AuthServerRefreshTokenData:
    user_id: UUID
    jti: str
    fingerprint: Fingerprint | None
    created_at: datetime


class RefreshTokenPayload(TypedDict):
    sub: str
    jti: UUID


@dataclass
class AuthServerRefreshTokenWithData(AuthServerRefreshTokenData):
    token: AuthServerRefreshToken


class AuthServerTokens(TypedDict):
    access_token: AuthServerAccessToken
    refresh_token: AuthServerRefreshToken
