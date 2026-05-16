import logging
from dataclasses import dataclass

from application.common.interfaces.role_repo import RoleRepository
from application.common.uow import Uow
from domain.entities.role.value_objects import RoleBaseScopes, RoleID, RoleName
from domain.exceptions.role import RoleNotFoundError


@dataclass
class UpdateRoleCommand:
    role_id: int
    new_name: str | None
    new_base_scopes: dict[str, str] | None
    new_is_base: bool | None


logger = logging.getLogger(__name__)


class UpdateRoleHandler:
    def __init__(self, role_repo: RoleRepository, uow: Uow):
        self.role_repo = role_repo
        self.uow = uow

    async def handle(self, command: UpdateRoleCommand):
        role = await self.role_repo.get_by_id(RoleID(command.role_id))
        if not role:
            raise RoleNotFoundError

        updates = {
            "base_scopes": (
                RoleBaseScopes.create(command.new_base_scopes)
                if command.new_base_scopes
                else None
            ),
            "name": (RoleName(command.new_name) if command.new_name else None),
            "is_base": (
                command.new_is_base if command.new_base_scopes else None
            ),
        }
        logger.info("Updating role with updates: %s", updates)

        for attr, value in updates.items():
            if value is not None:
                setattr(role, attr, value)

        await self.role_repo.save(role)
        await self.uow.commit()
