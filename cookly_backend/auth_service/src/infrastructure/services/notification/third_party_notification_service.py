from dataclasses import asdict, dataclass
from typing import Literal

from nats.aio.client import Client
from redis.asyncio import Redis

from application.third_party_auth.common.third_party_notification_service import (
    ThirdPartyNotificationService,
)
from infrastructure.external_services.message_routing.config import NatsConfig
from infrastructure.external_services.message_routing.nats_utils import (
    send_via_nats,
)


@dataclass
class ThirdPartyRegisterCommand:
    email: str
    generated_password: str
    provider: Literal["yandex"]


class ThirdPartyNotificationServiceImpl(ThirdPartyNotificationService):
    def __init__(
        self,
        redis: Redis,
        nats_client: Client,
        nats_config: NatsConfig,
    ):
        self._nats_client = nats_client
        self._nats_config = nats_config
        self._redis = redis

    async def send_register_notification(
        self, command: ThirdPartyRegisterCommand
    ) -> None:
        await send_via_nats(
            self._nats_client,
            self._nats_config.third_party_register_sub,
            data=asdict(command),
        )
