from application.common.client_token_types import ClientRefreshToken
from application.common.interfaces.http_auth import HttpClientService


class RevokeClientTokenHandler:
    def __init__(self, auth_service: HttpClientService):
        self.auth_service = auth_service

    async def handle(self, refresh_token: ClientRefreshToken) -> None:
        await self.auth_service.revoke(refresh_token)
