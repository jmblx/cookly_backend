from dataclasses import dataclass

from application.common.interfaces.user_repo import UserRepository
from application.common.uow import Uow
from application.user.reset_pwd.service import (
    ResetPasswordToken,
    ResetPwdService,
)
from core.exceptions.user_password.exceptions import (
    InvalidResetPasswordToken,
)
from domain.common.services.pwd_service import PasswordHasher
from domain.entities.user.value_objects import RawPassword, UserID


@dataclass
class ResetPasswordWithTokenCommand:
    reset_token: str
    new_pwd: str


class ResetPasswordWithTokenHandler:
    def __init__(
        self,
        uow: Uow,
        user_repo: UserRepository,
        reset_pwd_service: ResetPwdService,
        hash_service: PasswordHasher,
    ):
        self.uow = uow
        self.user_repo = user_repo
        self.reset_pwd_service = reset_pwd_service
        self.hash_service = hash_service

    async def handle(self, command: ResetPasswordWithTokenCommand) -> None:
        user_id = await self.reset_pwd_service.get_user_id_from_reset_token(
            ResetPasswordToken(command.reset_token)
        )
        if not user_id:
            raise InvalidResetPasswordToken()

        user = await self.user_repo.get_by_id(UserID(user_id))
        user.hashed_password = self.hash_service.hash_password(
            RawPassword(command.new_pwd)
        )

        await self.user_repo.save(user)
        await self.uow.commit()
        await self.reset_pwd_service.delete_reset_token(
            ResetPasswordToken(command.reset_token)
        )
