import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.interfaces.email_confirmation_service import (
    EmailConfirmationServiceI,
)
from application.common.interfaces.user_repo import UserRepository
from application.common.uow import Uow
from domain.entities.user.value_objects import UserID


@dataclass
class ConfirmEmailCommand:
    email_confirmation_token: str


logger = logging.getLogger(__name__)


class ConfirmEmailHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        uow: Uow,
        email_confirmation_service: EmailConfirmationServiceI,
    ) -> None:
        self.user_repo = user_repo
        self.uow = uow
        self.email_confirmation_service = email_confirmation_service

    async def handle(self, command: ConfirmEmailCommand) -> None:
        user_id: UUID = (
            await self.email_confirmation_service.get_user_id_by_conf_token(
                command.email_confirmation_token
            )
        )
        logger.info(
            "user_id: %s \nconf_token: %s",
            user_id,
            command.email_confirmation_token,
        )
        user = await self.user_repo.get_by_id(user_id=UserID(user_id))
        user.is_email_confirmed = True
        await self.user_repo.save(user)
        await self.uow.commit()
        await self.email_confirmation_service.delete_confirmation_token(
            command.email_confirmation_token
        )
