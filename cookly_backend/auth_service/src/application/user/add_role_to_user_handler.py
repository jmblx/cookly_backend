from dataclasses import dataclass
from uuid import UUID

from application.common.interfaces.role_repo import RoleRepository
from application.common.interfaces.user_repo import UserRepository
from domain.entities.role.value_objects import RoleID
from domain.entities.user.value_objects import UserID
from domain.exceptions.role import RoleNotFoundError


@dataclass
class AddRoleToUserCommand:
    user_id: UUID
    role_id: int


class AddRoleToUserHandler:
    def __init__(
        self, user_repository: UserRepository, role_repository: RoleRepository
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def handle(self, command: AddRoleToUserCommand):
        role = await self.role_repository.get_by_id(RoleID(command.role_id))
        if role is None:
            raise RoleNotFoundError()
        await self.user_repository.add_roles_to_user(
            UserID(command.user_id), [role.id]
        )
