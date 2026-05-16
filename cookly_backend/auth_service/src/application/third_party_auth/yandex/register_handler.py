from dataclasses import dataclass
from typing import cast

from application.auth_as.register_user_auth_server.confirm_registration_handler import CompleteRegisterUserResult
from application.common.interfaces.http_auth import HttpAuthServerService
from application.common.interfaces.user_repo import UserRepository
from application.common.uow import Uow
from application.third_party_auth.common.idp import OAuth2Token
from application.third_party_auth.common.password_generation import (
    generate_random_password,
)
from application.third_party_auth.common.third_party_notification_service import (
    ThirdPartyNotificationService,
    ThirdPartyRegisterCommand,
)
from application.third_party_auth.yandex.idp import YandexIdentityProvider
from domain.common.services.pwd_service import PasswordHasher
from domain.entities.user.model import User
from domain.exceptions.user import UserAlreadyExistsError


@dataclass
class YandexRegisterCommand:
    yandex_token: OAuth2Token


class YandexRegisterHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        hash_service: PasswordHasher,
        uow: Uow,
        notification_service: ThirdPartyNotificationService,
        auth_server_service: HttpAuthServerService,
        yandex_idp: YandexIdentityProvider,
    ):
        self.user_repository = user_repo
        self.hash_service = hash_service
        self.uow = uow
        self.notification_service = notification_service
        self.auth_server_service = auth_server_service
        self.yandex_idp = yandex_idp

    async def handle(
        self, command: YandexRegisterCommand
    ) -> CompleteRegisterUserResult:
        email = await self.yandex_idp.get_yandex_user_email(
            command.yandex_token
        )
        existing_user = await self.user_repository.get_by_email(
            email=email,
        )
        if existing_user:
            raise UserAlreadyExistsError(existing_user.email.value)
        generated_password = generate_random_password()
        user_id = User.generate_id()
        user = User.create(
            user_id=user_id,
            email=email.value,
            raw_password=generated_password,
            password_hasher=self.hash_service,
        )
        await self.user_repository.save(user)
        auth_tokens = await self.auth_server_service.create_and_save_tokens(
            user
        )
        notify_data = ThirdPartyRegisterCommand(
            email=email.value,
            generated_password=generated_password,
            provider="yandex",
        )
        await self.notification_service.send_register_notification(notify_data)
        await self.uow.commit()
        result = {**auth_tokens, "user_id": user_id}
        return cast(CompleteRegisterUserResult, result)
