import logging
from dataclasses import dataclass

from application.client.common.client_repo import ClientRepository
from application.common.uow import Uow
from application.dtos.client import ClientCreateDTO
from domain.entities.client.model import Client
from domain.entities.client.value_objects import ClientTypeEnum


@dataclass
class RegisterClientCommand:
    name: str
    base_url: str
    allowed_redirect_urls: list[str]
    type: ClientTypeEnum


class RegisterClientHandler:
    def __init__(self, client_repo: ClientRepository, uow: Uow):
        self.client_repo = client_repo
        self.uow = uow

    async def handle(self, command: RegisterClientCommand) -> ClientCreateDTO:
        client = Client.create(
            name=command.name,
            base_url=command.base_url,
            allowed_redirect_urls=command.allowed_redirect_urls,
            type=command.type,
        )
        client_dto = await self.client_repo.save(client)
        await self.uow.commit()
        logger = logging.getLogger(__name__)
        logger.info(f"Client {client_dto.client_id} created")
        return client_dto
