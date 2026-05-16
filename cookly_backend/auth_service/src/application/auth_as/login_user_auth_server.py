import logging
from dataclasses import dataclass

from application.common.auth_server_token_types import AuthServerTokens
from application.common.id_provider import UserIdentityProvider
from application.common.interfaces.http_auth import HttpAuthServerService
from application.common.interfaces.user_repo import UserRepository
from application.common.services.multiacc import change_active_account_id
from domain.common.services.pwd_service import PasswordHasher
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email, RawPassword, UserID
from domain.exceptions.user import UserNotFoundByEmailError

logger = logging.getLogger(__name__)


@dataclass
class AuthenticateUserCommand:
    email: str
    password: str


class LoginUserHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        auth_server_service: HttpAuthServerService,
        idp: UserIdentityProvider,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.auth_server_service = auth_server_service
        self.idp = idp

    async def handle(
        self, command: AuthenticateUserCommand
    ) -> tuple[AuthServerTokens, UserID | None, UserID | None]:
        """
        :param command: AuthenticateUserCommand
        :return: возвращаем токены и аккаунт пользователя
         который был активным до логина в случае смены активного аккаунта
        """
        new_active_user: User | None = await self.user_repository.get_by_email(
            Email(command.email)
        )
        if not new_active_user:
            raise UserNotFoundByEmailError(command.email)
        new_active_user.check_pwd(
            RawPassword(command.password), password_hasher=self.password_hasher
        )
        tokens = await self.auth_server_service.create_and_save_tokens(
            new_active_user, is_admin=new_active_user.is_admin
        )
        previous_account_id, new_active_account_id = (
            await change_active_account_id(self.idp, new_active_user)
        )
        if new_active_user:
            new_active_account_id = new_active_account_id or new_active_user.id
        return tokens, previous_account_id, new_active_account_id
