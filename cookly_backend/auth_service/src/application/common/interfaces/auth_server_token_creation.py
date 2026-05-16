from abc import ABC, abstractmethod
from uuid import UUID

from application.common.auth_server_token_types import (
    AuthServerAccessToken,
    AuthServerRefreshTokenWithData,
    Fingerprint,
)


class AuthServerTokenCreationService(ABC):
    """Абстракция для создания токенов."""

    @abstractmethod
    def create_auth_server_access_token(
        self, user_id: UUID, is_admin: bool
    ) -> AuthServerAccessToken:
        """Создание AuthServerAccessToken."""

    @abstractmethod
    async def create_auth_server_refresh_token(
        self, user_id: UUID, fingerprint: Fingerprint
    ) -> AuthServerRefreshTokenWithData:
        """Создание AuthServerRefreshToken."""
