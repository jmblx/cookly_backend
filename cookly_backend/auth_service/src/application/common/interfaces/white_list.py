from abc import ABC, abstractmethod
from uuid import UUID

from application.common.auth_server_token_types import (
    AuthServerRefreshTokenData,
    AuthServerRefreshTokenWithData,
)
from application.common.client_token_types import (
    ClientRefreshTokenData,
    ClientRefreshTokenWithData,
)


class AuthServerTokenWhitelistService(ABC):
    """Интерфейс для auth_server, требует fingerprint."""

    @abstractmethod
    async def is_fingerprint_matching(
        self, jti: UUID, fingerprint: str
    ) -> bool: ...

    @abstractmethod
    async def replace_refresh_token(
        self, refresh_token_data: AuthServerRefreshTokenWithData, limit: int
    ) -> None: ...

    @abstractmethod
    async def get_refresh_token_data(
        self, jti: UUID
    ) -> AuthServerRefreshTokenData | None: ...

    @abstractmethod
    async def remove_old_tokens(
        self, user_id: UUID, fingerprint: str, limit: int
    ) -> None: ...

    @abstractmethod
    async def remove_token(self, jti: UUID) -> None: ...

    @abstractmethod
    async def remove_tokens_except_current(
        self, jti: UUID, user_id: UUID
    ) -> None: ...


class ClientTokenWhitelistService(ABC):
    """Интерфейс для client, без fingerprint."""

    @abstractmethod
    async def replace_refresh_token(
        self, refresh_token_data: ClientRefreshTokenWithData, limit: int
    ) -> None: ...

    @abstractmethod
    async def get_refresh_token_data(
        self, jti: UUID
    ) -> ClientRefreshTokenData | None: ...

    @abstractmethod
    async def remove_old_tokens(self, user_id: UUID, limit: int) -> None: ...

    @abstractmethod
    async def remove_token(self, jti: UUID) -> None: ...

    @abstractmethod
    async def remove_tokens_except_current(
        self, jti: UUID, user_id: UUID
    ) -> None: ...
