from nats.aio.client import Client

from application.common.interfaces.notify_service import NotifyService
from application.user.reset_pwd.service import ResetPasswordCode
from core.di.providers.nats_provider import NatsConfig
from infrastructure.external_services.message_routing.nats_utils import (
    send_via_nats,
)


class NotifyServiceImpl(NotifyService):
    def __init__(self, nats_client: Client, nats_config: NatsConfig):
        self._nats_client = nats_client
        self._nats_config = nats_config

    async def pwd_reset_notify(
        self, user_email: str, reset_pwd_token: ResetPasswordCode
    ) -> None:
        await send_via_nats(
            nats_client=self._nats_client,
            subject=self._nats_config.reset_pwd_email_sub,
            data={
                "reset_password_token": reset_pwd_token,
                "email": user_email,
            },
        )
