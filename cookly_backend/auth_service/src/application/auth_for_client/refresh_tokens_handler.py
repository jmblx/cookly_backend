from application.auth_as.common.scopes_service import ScopesService
from application.common.auth_server_token_types import (
    Fingerprint,
)
from application.common.client_token_types import ClientTokens
from application.common.id_provider import ClientIdentityProvider
from application.common.interfaces.http_auth import HttpClientService
from application.common.interfaces.jwt_service import JWTService
from application.common.interfaces.role_repo import RoleRepository
from application.common.interfaces.user_repo import UserRepository


class RefreshClientTokensHandler:
    def __init__(
        self,
        auth_service: HttpClientService,
        jwt_service: JWTService,
        fingerprint: Fingerprint,
        scopes_service: ScopesService,
        role_repo: RoleRepository,
        user_repo: UserRepository,
    ):
        self.auth_service = auth_service
        self.fingerprint = fingerprint
        self.scopes_service = scopes_service
        self.role_repo = role_repo
        self.jwt_service = jwt_service
        self.user_repo = user_repo

    def _decode_token(self, token: str) -> dict:
        return self.jwt_service.decode(token)

    async def handle(
        self, refresh_token: str
    ) -> ClientTokens:
        payload = self._decode_token(refresh_token)

        user_id = payload["sub"]
        user = await self.user_repo.get_by_id(user_id)
        client_id = payload["client_id"]
        rs_ids = payload["rs_ids"]
        print(payload)
        user_roles = await self.role_repo.get_user_roles_by_rs_ids(
            user.id, rs_ids
        )
        new_scopes = self.scopes_service.calculate_full_user_scopes_for_client(
            user_roles
        )
        return await self.auth_service.create_and_save_tokens(
            user, new_scopes, client_id, rs_ids
        )
