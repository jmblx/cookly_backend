from uuid import UUID

from application.common.auth_server_token_types import Fingerprint
from application.common.client_token_types import (
    ClientAccessTokenPayload,
    ClientRefreshToken,
    ClientTokens,
)
from application.common.interfaces.client_token_creation import (
    ClientTokenCreationService,
)
from application.common.interfaces.http_auth import HttpClientService
from application.common.interfaces.jwt_service import JWTService
from application.common.interfaces.white_list import (
    ClientTokenWhitelistService,
)
from application.common.services.auth_code import AuthorizationCodeStorage
from domain.entities.user.model import User
from infrastructure.services.auth.config import JWTSettings


class HttpClientServiceImpl(HttpClientService):
    def __init__(
        self,
        jwt_service: JWTService,
        token_creation_service: ClientTokenCreationService,
        token_whitelist_service: ClientTokenWhitelistService,
        jwt_settings: JWTSettings,
        auth_code_storage: AuthorizationCodeStorage,
        fingerprint: Fingerprint,
    ):
        self.jwt_service = jwt_service
        self.token_creation_service = token_creation_service
        self.token_whitelist_service = token_whitelist_service
        self.jwt_settings = jwt_settings
        self.auth_code_storage = auth_code_storage
        self.fingerprint = fingerprint

    def _get_token_jti(self, refresh_token: ClientRefreshToken) -> UUID:
        payload = self.jwt_service.decode(refresh_token)
        return payload["jti"]

    async def revoke(self, refresh_token: ClientRefreshToken) -> None:
        jti = self._get_token_jti(refresh_token)
        await self.token_whitelist_service.remove_token(jti)

    async def invalidate_other_tokens(
        self, refresh_token: ClientRefreshToken
    ) -> None:
        payload: ClientAccessTokenPayload = self.jwt_service.decode(
            refresh_token
        )
        jti = payload["jti"]
        user_id: UUID = payload["sub"]  # type: ignore
        await self.token_whitelist_service.remove_tokens_except_current(
            jti, user_id
        )

    async def create_and_save_tokens(
        self,
        user: User,
        user_scopes: list[str],
        client_id: int,
        rs_ids: list[int] | None,
    ) -> ClientTokens:
        """Создаёт и сохраняет токены."""
        user_id: UUID = user.id.value
        access_token = self.token_creation_service.create_client_access_token(
            user_id, user_scopes, client_id, rs_ids
        )
        refresh_token_data = (
            await self.token_creation_service.create_client_refresh_token(
                user_id, client_id, rs_ids
            )
        )
        await self.token_whitelist_service.replace_refresh_token(
            refresh_token_data,
            self.jwt_settings.refresh_token_by_user_limit,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_data.token,
        }
