from dataclasses import dataclass, field

from application.common.interfaces.role_repo import RoleRepository
from application.common.uow import Uow
from domain.entities.role.model import Role
from domain.entities.role.value_objects import RoleID


@dataclass
class CreateRoleCommand:
    name: str
    base_scopes: dict[str, str]
    rs_id: int
    is_base: bool = field(default=False)


class CreateRoleHandler:
    def __init__(self, role_repo: RoleRepository, uow: Uow) -> None:
        self.role_repo = role_repo
        self.uow = uow

    async def handle(self, command: CreateRoleCommand) -> int:
        role = Role.create(
            name=command.name,
            base_scopes=command.base_scopes,
            rs_id=command.rs_id,
            is_base=command.is_base,
        )
        role_id: RoleID = await self.role_repo.save(role)
        await self.uow.commit()
        return role_id
