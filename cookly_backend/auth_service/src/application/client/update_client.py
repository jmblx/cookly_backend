from dataclasses import dataclass

from application.client.common.client_repo import ClientRepository
from application.common.uow import Uow
from domain.entities.client.model import Client
from domain.entities.client.value_objects import (
    AllowedRedirectUrls,
    ClientBaseUrl,
    ClientID,
    ClientName,
    ClientType,
    ClientTypeEnum,
)
from domain.exceptions.client import ClientNotFound


@dataclass(frozen=True)
class UpdateClientCommand:
    client_id: int
    name: str | None
    base_url: str | None
    allowed_redirect_urls: list[str] | None
    type: ClientTypeEnum | None


class UpdateClientCommandHandler:
    def __init__(self, client_repo: ClientRepository, uow: Uow):
        self.client_repo = client_repo
        self.uow = uow

    async def handle(self, command: UpdateClientCommand) -> None:
        client: Client | None = await self.client_repo.get_by_id(
            ClientID(command.client_id)
        )
        if not client:
            raise ClientNotFound()

        if command.name:
            client.rename(command.name)
        updates = {
            "base_url": (
                ClientBaseUrl(command.base_url) if command.base_url else None
            ),
            "allowed_redirect_urls": (
                AllowedRedirectUrls(command.allowed_redirect_urls)
                if command.allowed_redirect_urls
                else None
            ),
            "type": (ClientType(command.type) if command.type else None),
        }
        for attr, value in updates.items():
            if value is not None:
                setattr(client, attr, value)

        await self.client_repo.save(client)
        await self.uow.commit()
