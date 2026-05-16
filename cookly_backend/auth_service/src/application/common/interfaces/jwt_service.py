from abc import ABC, abstractmethod
from datetime import timedelta
from uuid import UUID

from application.common.auth_server_token_types import (
    AuthServerAccessTokenPayload,
    BaseToken,
    JwtToken,
)
from application.common.client_token_types import ClientAccessTokenPayload


class JWTService(ABC):
    """Абстракция для работы с JWT токенами."""

    @abstractmethod
    def encode(
        self,
        payload: dict[str, int | str | UUID],
        expire_minutes: int | None = None,
        expire_timedelta: timedelta | None = None,
    ) -> JwtToken:
        """Создание JWT токена с заданным сроком действия."""

    @abstractmethod
    def decode(
        self, token: BaseToken
    ) -> AuthServerAccessTokenPayload | ClientAccessTokenPayload:
        """Декодирование JWT токена."""
