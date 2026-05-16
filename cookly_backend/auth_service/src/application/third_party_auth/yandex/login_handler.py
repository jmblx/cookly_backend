from dataclasses import dataclass

from application.common.auth_server_token_types import AuthServerTokens
from application.common.id_provider import UserIdentityProvider
from application.common.interfaces.http_auth import HttpAuthServerService
from application.common.services.multiacc import change_active_account_id
from application.third_party_auth.common.idp import OAuth2Token
from application.third_party_auth.yandex.idp import YandexIdentityProvider
from domain.entities.user.value_objects import UserID
from domain.exceptions.user import ThirdPartyUserNotRegisteredError


@dataclass
class YandexLoginCommand:
    yandex_token: OAuth2Token


class YandexLoginHandler:
    def __init__(
        self,
        auth_server_service: HttpAuthServerService,
        yandex_id_provider: YandexIdentityProvider,
        base_idp: UserIdentityProvider,
    ):
        self.auth_server_service = auth_server_service
        self.yandex_id_provider = yandex_id_provider
        self.base_idp = base_idp

    async def handle(
        self, command: YandexLoginCommand
    ) -> tuple[AuthServerTokens, UserID | None, UserID | None]:
        new_active_user_email = await self.yandex_id_provider.get_yandex_user_email(command.yandex_token)
        new_active_user = await self.yandex_id_provider.get_current_user(
            command.yandex_token
        )
        if new_active_user_email and not new_active_user:
            raise ThirdPartyUserNotRegisteredError(new_active_user_email)
        tokens = await self.auth_server_service.create_and_save_tokens(
            new_active_user, is_admin=new_active_user.is_admin
        )
        previous_account_id, new_account_id = await change_active_account_id(
            self.base_idp, new_active_user
        )
        return tokens, previous_account_id, new_account_id
