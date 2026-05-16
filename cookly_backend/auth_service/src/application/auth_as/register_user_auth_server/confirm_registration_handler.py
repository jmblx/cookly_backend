from dataclasses import dataclass
from typing import cast
from uuid import UUID

from redis.asyncio import Redis

from application.common.auth_server_token_types import (
    AuthServerTokens,
)
from application.common.interfaces.email_confirmation_service import (
    EmailConfirmationServiceI,
)
from application.common.interfaces.http_auth import HttpAuthServerService
from application.common.interfaces.user_repo import UserRepository
from application.common.uow import Uow
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email, RawPassword, HashedPassword
from domain.exceptions.user import UserAlreadyExistsError, UnauthenticatedUserError


@dataclass
class CompleteRegisterUserCommand:
    email: str
    confirmation_token: str


class CompleteRegisterUserResult(AuthServerTokens):
    user_id: UUID


class CompleteRegisterUserHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        uow: Uow,
        email_confirmation_service: EmailConfirmationServiceI,
        auth_server_service: HttpAuthServerService,
        redis: Redis,
    ):
        self.user_repository = user_repo
        self.uow = uow
        self.email_confirmation_service = email_confirmation_service
        self.auth_server_service = auth_server_service
        self.redis = redis

    async def handle(self, command: CompleteRegisterUserCommand) -> CompleteRegisterUserResult:
        existing_user = await self.user_repository.get_by_email(
            Email(command.email)
        )
        if existing_user:
            raise UserAlreadyExistsError(existing_user.email.value)

        token_data = await self.email_confirmation_service.get_data_by_token(command.confirmation_token)
        if token_data.email != command.email:
            raise UnauthenticatedUserError()

        user_id = User.generate_id()

        user = User.create_with_hashed_password(
            user_id=user_id,
            email=command.email,
            hashed_password=HashedPassword(token_data.password),
            is_email_confirmed=True,
        )
        await self.user_repository.save(user)
        auth_tokens = await self.auth_server_service.create_and_save_tokens(
            user
        )

        await self.uow.commit()
        result = {**auth_tokens, "user_id": user_id}
        await self.email_confirmation_service.delete_data_by_token(command.confirmation_token)
        return cast(CompleteRegisterUserResult, result)
