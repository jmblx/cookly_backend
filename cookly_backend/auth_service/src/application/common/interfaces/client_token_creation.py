from abc import ABC, abstractmethod
from uuid import UUID

from application.common.client_token_types import (
    ClientAccessToken,
    ClientRefreshTokenWithData,
)


class ClientTokenCreationService(ABC):
    """Абстракция для создания токенов."""

    @abstractmethod
    def create_client_access_token(
        self, user_id: UUID, user_scopes: list[str], client_id: int, rs_ids: list[int]
    ) -> ClientAccessToken:
        """Создание AuthServerAccessToken."""

    @abstractmethod
    async def create_client_refresh_token(
        self, user_id: UUID, client_id, rs_ids
    ) -> ClientRefreshTokenWithData:
        """Создание AuthServerRefreshToken."""
