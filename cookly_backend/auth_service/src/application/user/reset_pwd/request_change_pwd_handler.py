import secrets
import string
from dataclasses import dataclass
from typing import cast

from application.common.interfaces.notify_service import NotifyService
from application.common.interfaces.user_repo import UserRepository
from application.user.reset_pwd.service import (
    ResetPasswordCode,
    ResetPwdService,
)
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email


@dataclass
class RequestChangePasswordCommand:
    email: str


def generate_6_digit_code():
    alphabet = string.digits
    return "".join(secrets.choice(alphabet) for _ in range(6))


class RequestChangePasswordHandler:
    def __init__(
        self,
        notify_service: NotifyService,
        user_repository: UserRepository,
        reset_pwd_service: ResetPwdService,
    ):
        self.notify_service = notify_service
        self.user_repository = user_repository
        self.reset_pwd_service = reset_pwd_service

    async def handle(self, command: RequestChangePasswordCommand) -> bool:
        # if command.email:
        user: User = await self.user_repository.get_by_email(
            Email(command.email)
        )
        reset_pwd_code: ResetPasswordCode = cast(
            ResetPasswordCode, generate_6_digit_code()
        )
        await self.reset_pwd_service.save_password_reset_code(
            user.id.value, reset_pwd_code
        )
        await self.notify_service.pwd_reset_notify(
            command.email, reset_pwd_code
        )
        return True
