import logging
from abc import ABC, abstractmethod
from uuid import UUID

from application.common.auth_server_token_types import (
    AuthServerAccessToken,
    AuthServerRefreshToken,
    Fingerprint,
    NonActiveRefreshTokens,
)
from application.common.client_token_types import (
    ClientAccessToken,
    ClientRefreshToken,
)
from application.common.interfaces.jwt_service import JWTService
from application.common.interfaces.user_repo import UserRepository
from application.common.interfaces.white_list import (
    AuthServerTokenWhitelistService,
    ClientTokenWhitelistService,
)
from domain.entities.client.value_objects import ClientID
from domain.entities.resource_server.value_objects import ResourceServerID
from domain.entities.user.model import User
from domain.entities.user.value_objects import UserID
from domain.exceptions.auth import InvalidTokenError


class UserIdentityProvider(ABC):
    @abstractmethod
    async def get_current_user_id(self) -> UserID | None: ...

    @abstractmethod
    async def get_current_user(self, validate_refresh: bool = True) -> User: ...

    @abstractmethod
    async def get_unvalidated_user_id(self, ) -> UserID | None: ...


class ClientIdentityProvider(UserIdentityProvider):
    @abstractmethod
    def get_current_client_id(self) -> ClientID: ...

    @abstractmethod
    def get_current_rs_ids(self) -> list[ResourceServerID]: ...

    @abstractmethod
    def get_current_user_scopes(self) -> list[str]: ...


logger = logging.getLogger(__name__)


class BaseTokenProvider(ABC):
    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service
        self._decoded_tokens: dict[str, dict] = {}

    def _decode_token(self, token_name: str, token_value: str) -> dict:
        if token_name not in self._decoded_tokens:
            self._decoded_tokens[token_name] = self.jwt_service.decode(
                token_value
            )
        return self._decoded_tokens[token_name]


class UserIdentityProviderImpl(UserIdentityProvider, BaseTokenProvider):
    def __init__(
        self,
        access_token: AuthServerAccessToken,
        refresh_token: AuthServerRefreshToken,
        non_active_tokens: NonActiveRefreshTokens,
        jwt_service: JWTService,
        user_repo: UserRepository,
        token_whitelist_service: AuthServerTokenWhitelistService,
        fingerprint: Fingerprint,
    ):
        super().__init__(jwt_service)
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.non_active_tokens = non_active_tokens
        self.user_repo = user_repo
        self.token_whitelist_service = token_whitelist_service
        self.fingerprint = fingerprint

    def _get_refresh_token_jti(self) -> UUID:
        payload = self._decode_token("refresh_token", self.refresh_token)
        return payload["jti"]

    async def _validate_refresh_token(self, jti: UUID) -> UserID:
        token_data = await self.token_whitelist_service.get_refresh_token_data(
            jti
        )
        if not token_data or token_data.fingerprint and token_data.fingerprint != self.fingerprint:
            raise InvalidTokenError()
        return UserID(token_data.user_id)

    async def get_unvalidated_user_id(self, ) -> UserID | None:
        payload = self._decode_token("access_token", self.access_token)
        return UserID(payload["sub"])

    async def get_current_user_id(self, ) -> UserID | None:
        if not self.refresh_token:
            return None
        jti = self._get_refresh_token_jti()
        try:
            return await self._validate_refresh_token(jti)
        except InvalidTokenError:
            return None

    async def get_current_user(self, validate_refresh: bool = True) -> User:
        user_id = await self.get_current_user_id() if validate_refresh else await self.get_unvalidated_user_id()
        return await self.user_repo.get_by_id(user_id)


class ClientIdentityProviderImpl(ClientIdentityProvider, BaseTokenProvider):
    def __init__(
        self,
        client_access_token: ClientAccessToken,
        client_refresh_token: ClientRefreshToken,
        jwt_service: JWTService,
        user_repo: UserRepository,
        token_whitelist_service: ClientTokenWhitelistService,
        fingerprint: Fingerprint,
    ):
        super().__init__(jwt_service)
        self.client_access_token = client_access_token
        self.client_refresh_token = client_refresh_token
        self.user_repo = user_repo
        self.token_whitelist_service = token_whitelist_service
        self.fingerprint = fingerprint
        if self.client_access_token:
            self._client_access_token_payload = self._decode_token(
                "client_access_token", self.client_access_token
            )
        if self.client_refresh_token:
            self._client_refresh_token_payload = self._decode_token(
                "client_refresh_token", self.client_refresh_token
            )

    def get_current_client_id(self) -> ClientID:
        return self._client_refresh_token_payload["client_id"]

    def get_current_rs_ids(self) -> list[ResourceServerID]:
        return self._client_refresh_token_payload["rs_ids"]

    def _get_refresh_token_jti(self) -> UUID:
        return self._client_refresh_token_payload["jti"]

    def get_current_user_scopes(self) -> list[str]:
        return self._client_access_token_payload["scopes"]

    async def get_current_user_id(self) -> UserID | None:
        jti = self._get_refresh_token_jti()
        token_data = await self.token_whitelist_service.get_refresh_token_data(
            jti
        )
        logger.info("code data: %s", token_data)
        if not token_data:
            return None
        return UserID(token_data.user_id)

    async def get_unvalidated_user_id(self, ) -> UserID | None:
        payload = self._decode_token("client_access_token", self.client_access_token)
        return UserID(payload["sub"])

    async def get_current_user(self, validate_refresh: bool = True) -> User:
        user_id = await self.get_current_user_id() if validate_refresh else await self.get_unvalidated_user_id()
        return await self.user_repo.get_by_id(user_id)
