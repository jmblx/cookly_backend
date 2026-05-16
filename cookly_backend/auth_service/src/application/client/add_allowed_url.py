from dataclasses import dataclass

from application.client.common.client_repo import ClientRepository
from application.common.uow import Uow
from domain.entities.client.model import Client
from domain.entities.client.value_objects import ClientID
from domain.exceptions.client import ClientNotFound


@dataclass
class AddAllowedRedirectUrlCommand:
    new_url: str


class AddAllowedRedirectUrlCommandHandler:
    def __init__(self, client_repo: ClientRepository, uow: Uow) -> None:
        self.client_repo = client_repo
        self.uow = uow

    async def handle(
        self, command: AddAllowedRedirectUrlCommand, client_id: int
    ) -> None:
        client: Client | None = await self.client_repo.get_by_id(
            ClientID(client_id)
        )
        if not client:
            raise ClientNotFound()
        client.add_allowed_redirect_url(command.new_url)
        await self.uow.commit()
