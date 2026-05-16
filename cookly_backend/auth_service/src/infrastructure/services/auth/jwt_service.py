from datetime import datetime, timedelta
from typing import cast
from uuid import UUID

import jwt
from pytz import timezone

from application.common.auth_server_token_types import (
    AuthServerAccessTokenPayload,
    BaseToken,
    JwtToken,
)
from application.common.client_token_types import ClientAccessTokenPayload
from application.common.interfaces.jwt_service import JWTService
from domain.exceptions.auth import InvalidTokenError, TokenExpiredError
from infrastructure.services.auth.config import JWTSettings


class JWTServiceImpl(JWTService):
    """Реализация сервиса работы с JWT токенами."""

    def __init__(self, auth_settings: JWTSettings):
        self.auth_settings = auth_settings

    def encode(
        self,
        payload: dict[str, int | str | UUID],
        expire_minutes: int | None = None,
        expire_timedelta: timedelta | None = None,
    ) -> JwtToken:
        """Создаёт JWT токен с указанным сроком действия."""
        tz = timezone("Europe/Moscow")
        now = datetime.now(tz)

        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(
                minutes=expire_minutes
                or self.auth_settings.access_token_expire_minutes
            )
        token = jwt.encode(
            {**payload, "exp": expire, "iat": now},
            self.auth_settings.private_key,
            algorithm=self.auth_settings.algorithm,
        )
        return {
            "code": BaseToken(token),
            "created_at": now,
            "expires_at": expire,
        }

    def decode(
        self, token: BaseToken
    ) -> AuthServerAccessTokenPayload | ClientAccessTokenPayload:
        """Декодирует JWT токен и возвращает его payload."""
        try:
            print(token)
            payload = jwt.decode(
                token,
                self.auth_settings.public_key,
                algorithms=[self.auth_settings.algorithm],
            )
            return cast(AuthServerAccessTokenPayload, payload)
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.DecodeError:
            raise InvalidTokenError()
