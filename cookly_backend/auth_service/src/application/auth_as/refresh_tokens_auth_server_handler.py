from application.common.auth_server_token_types import AuthServerTokens
from application.common.id_provider import UserIdentityProvider
from application.common.interfaces.http_auth import HttpAuthServerService


class RefreshTokensHandler:
    def __init__(
        self,
        auth_service: HttpAuthServerService,
        idp: UserIdentityProvider,
    ):
        self.auth_service = auth_service
        self.idp = idp

    async def handle(
        self,
    ) -> AuthServerTokens:
        user = await self.idp.get_current_user()
        return await self.auth_service.create_and_save_tokens(user)
