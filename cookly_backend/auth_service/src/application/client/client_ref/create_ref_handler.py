from dataclasses import dataclass

from application.client.client_ref.common.repo import RefRepository, SaveRefDTO
from domain.common.logic_types import UserScope
from application.common.uow import Uow
from application.resource_server.common.rs_repo import ResourceServerRepository
from domain.entities.client.ref_model import ClientRef


@dataclass
class RegisterRefCommand:
    name: str
    user_scopes: list[UserScope]
    rs_ids: list[int]
    client_id: int


class RegisterRefHandler:
    def __init__(self, ref_repo: RefRepository, rs_repo: ResourceServerRepository, uow: Uow):
        self.ref_repo = ref_repo
        self.rs_repo = rs_repo
        self.uow = uow

    async def handle(self, command: RegisterRefCommand) -> SaveRefDTO:
        resource_servers = await self.rs_repo.get_many_by_ids(command.rs_ids)
        ref = ClientRef.create(
            name=command.name,
            user_scopes=command.user_scopes,
            client_id=command.client_id,
            resource_servers=resource_servers
        )
        ref_dto = await self.ref_repo.save(ref)
        await self.uow.commit()
        return ref_dto
