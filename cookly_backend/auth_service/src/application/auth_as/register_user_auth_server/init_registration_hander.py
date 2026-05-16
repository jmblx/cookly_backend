from dataclasses import dataclass

from redis.asyncio import Redis

from application.common.interfaces.email_confirmation_service import (
    EmailConfirmationServiceI,
    UserRegisterNotifyData,
)
from application.common.interfaces.http_auth import HttpAuthServerService
from application.common.interfaces.user_repo import UserRepository
from application.common.uow import Uow
from application.user.reset_pwd.request_change_pwd_handler import generate_6_digit_code
from domain.common.services.pwd_service import PasswordHasher
from domain.entities.user.value_objects import Email, RawPassword
from domain.exceptions.user import UserAlreadyExistsError


@dataclass
class InitRegisterUserCommand:
    email: str
    password: str


class InitRegisterUserHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        hash_service: PasswordHasher,
        email_confirmation_service: EmailConfirmationServiceI,
    ):
        self.user_repository = user_repo
        self.hash_service = hash_service
        self.email_confirmation_service = email_confirmation_service

    async def handle(self, command: InitRegisterUserCommand) -> None:
        existing_user = await self.user_repository.get_by_email(
            Email(command.email)
        )
        if existing_user:
            raise UserAlreadyExistsError(existing_user.email.value)

        email_confirmation_token = generate_6_digit_code()
        password_hash = self.hash_service.hash_password(RawPassword(command.password))

        await self.email_confirmation_service.save_confirmation_data(
            email_confirmation_token, email=command.email, password_hash=password_hash
        )
        notify_data: UserRegisterNotifyData = {
            "email_confirmation_token": email_confirmation_token,
            "email": command.email,
        }
        await self.email_confirmation_service.email_register_notify(
            notify_data
        )
