import logging
from dataclasses import dataclass

from application.common.uow import Uow
from application.resource_server.common.rs_repo import ResourceServerRepository
from application.resource_server.dtos import ResourceServerCreateDTO
from domain.entities.resource_server.model import ResourceServer
from domain.entities.resource_server.value_objects import ResourceServerType

logger = logging.getLogger(__name__)


@dataclass
class RegisterResourceServerCommand:
    name: str
    type: ResourceServerType


class RegisterResourceServerHandler:
    def __init__(self, rs_repo: ResourceServerRepository, uow: Uow):
        self.rs_repo = rs_repo
        self.uow = uow

    async def handle(
        self, command: RegisterResourceServerCommand
    ) -> ResourceServerCreateDTO:
        rs = ResourceServer.create(
            name=command.name,
            type=command.type,
        )
        rs_dto = await self.rs_repo.save(rs)
        await self.uow.commit()
        return rs_dto
