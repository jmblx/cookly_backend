from dataclasses import dataclass

from application.common.auth_server_token_types import AuthServerRefreshToken
from application.common.interfaces.http_auth import HttpAuthServerService


@dataclass
class InvalidateOtherTokensCommand:
    refresh_token: AuthServerRefreshToken


class InvalidateOtherTokensHandler:
    def __init__(self, http_auth_service: HttpAuthServerService):
        self.http_auth_service = http_auth_service

    async def handle(self, command: InvalidateOtherTokensCommand) -> None:
        await self.http_auth_service.invalidate_other_tokens(
            command.refresh_token
        )
