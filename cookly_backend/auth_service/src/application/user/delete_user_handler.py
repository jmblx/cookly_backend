from dataclasses import dataclass
from uuid import UUID

from application.common.interfaces.user_repo import UserRepository
from application.common.uow import Uow
from domain.entities.user.value_objects import UserID
from domain.exceptions.user import UserNotFoundByIdError


@dataclass
class DeleteUserCommand:
    user_id: UUID


class DeleteUserHandler:
    def __init__(self, user_repository: UserRepository, uow: Uow):
        self.user_repository = user_repository
        self.uow = uow

    async def handle(self, command: DeleteUserCommand):
        user_id = UserID(command.user_id)
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundByIdError(str(user_id.value))
        await self.user_repository.delete(user)
        await self.uow.commit()
