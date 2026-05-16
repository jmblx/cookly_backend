from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from application.common.auth_server_token_types import (
    AuthServerTokens,
    Fingerprint,
)
from application.common.client_token_types import ClientTokens
from domain.entities.user.model import User

TokenType = TypeVar("TokenType")


class HttpService(ABC, Generic[TokenType]):
    @abstractmethod
    async def invalidate_other_tokens(self, refresh_token: TokenType) -> None:
        """
        Инвалидирует все токены пользователя, кроме текущего.
        """

    @abstractmethod
    async def revoke(self, refresh_token: TokenType) -> None:
        """
        Инвалидация AuthServerRefreshToken (logout пользователя).

        :param refresh_token: Токен, который необходимо аннулировать.
        """

    # @abstractmethod
    # async def invalidate_user_tokens(
    #         self, user: User
    # ) -> None:
    #     """
    #     Инвалидирует все активные токены пользователя.
    #
    #     Используется, например, при сбросе пароля или принудительном выходе.
    #     :param user: Экземпляр пользователя.
    #     """

    # @abstractmethod
    # async def list_active_tokens(
    #         self, user: User
    # ) -> list[dict]:
    #     """
    #     Возвращает список активных токенов пользователя.
    #
    #     Может использоваться для управления сессиями.
    #     :param user: Экземпляр пользователя.
    #     :return: Список активных токенов с метаданными.
    #     """


class HttpAuthServerService(HttpService[AuthServerTokens]):
    """Абстракция для сервиса аутентификации и управления токенами."""

    @abstractmethod
    async def create_and_save_tokens(
        self,
        user: User,
        fingerprint: Fingerprint | None = None,
        is_admin: bool = False,
    ) -> AuthServerTokens: ...


class HttpClientService(HttpService[ClientTokens]):
    @abstractmethod
    async def create_and_save_tokens(
        self,
        user: User,
        user_scopes: list[str],
        client_id: int,
        rs_ids: list[int] | None,
    ) -> ClientTokens: ...
