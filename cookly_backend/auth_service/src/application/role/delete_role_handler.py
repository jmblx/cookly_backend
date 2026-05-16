from dataclasses import dataclass

from application.common.interfaces.role_repo import RoleRepository
from application.common.uow import Uow
from domain.entities.role.value_objects import RoleID


@dataclass
class DeleteRoleCommand:
    role_id: int


class DeleteRoleHandler:
    def __init__(self, role_repo: RoleRepository, uow: Uow) -> None:
        self.role_repo = role_repo
        self.uow = uow

    async def handle(self, command: DeleteRoleCommand) -> None:
        role = await self.role_repo.get_by_id(RoleID(command.role_id))
        await self.role_repo.delete_role(role)
        await self.uow.commit()
