from dataclasses import dataclass

from application.common.interfaces.user_repo import UserRepository
from application.user.reset_pwd.service import (
    ResetPasswordCode,
    ResetPwdService,
)
from core.exceptions.user_password.exceptions import InvalidResetPasswordCode
from domain.entities.user.value_objects import Email


@dataclass
class VerifyResetCodeCommand:
    email: str
    code: str


@dataclass
class VerifyResetCodeResult:
    reset_token: str


class VerifyResetCodeHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        reset_pwd_service: ResetPwdService,
    ):
        self.user_repo = user_repository
        self.reset_pwd_service = reset_pwd_service

    async def handle(
        self, command: VerifyResetCodeCommand
    ) -> VerifyResetCodeResult:
        user = await self.user_repo.get_by_email(Email(command.email))
        code = ResetPasswordCode(command.code)

        user_id = await self.reset_pwd_service.get_user_id_from_reset_pwd_code(
            code
        )
        if not user_id or user_id != user.id.value:
            raise InvalidResetPasswordCode()

        token = await self.reset_pwd_service.generate_reset_token(
            user.id.value
        )
        await self.reset_pwd_service.delete_reset_pwd_code(code)

        return VerifyResetCodeResult(reset_token=token)
