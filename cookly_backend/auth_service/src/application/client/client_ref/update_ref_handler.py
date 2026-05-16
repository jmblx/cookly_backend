from dataclasses import dataclass

from application.client.client_ref.common.repo import RefRepository
from domain.common.logic_types import UserScope
from application.common.uow import Uow
from application.resource_server.common.rs_repo import ResourceServerRepository
from domain.entities.client.value_objects import UserScopes


@dataclass
class UpdateRefCommand:
    ref_id: int
    name: str | None
    user_scopes: list[UserScope] | None
    rs_ids: list[int] | None


class UpdateRefCommandHandler:
    def __init__(self, ref_repo: RefRepository, rs_repo: ResourceServerRepository, uow: Uow):
        self.ref_repo = ref_repo
        self.rs_repo = rs_repo
        self.uow = uow

    async def handle(self, command: UpdateRefCommand) -> None:
        ref = await self.ref_repo.get_by_id(command.ref_id)
        resource_servers = await self.rs_repo.get_many_by_ids(command.rs_ids)
        updates = {
            "name": command.name,
            "user_scopes": UserScopes(command.user_scopes),
            "resource_servers": resource_servers,
        }
        for attr, value in updates.items():
            if value is not None:
                setattr(ref, attr, value)

        if updates:
            await self.ref_repo.save(ref)
            await self.uow.commit()
