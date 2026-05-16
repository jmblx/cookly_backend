from uuid import UUID

from application.auth.common.errors import UnauthorizedError, UserNotFoundError
from application.common.errors.exceptions import PermissionDeniedError
from application.common.interfaces.idp_service import IDPService
from application.common.types import AccessToken, AccessTokenPayload
from domain.entities.value_objects import RECIPE_MODERATOR_ROLES
from infrastructure.db.gateways.user_gateway import UserGateway
from infrastructure.db.models.user import User
from infrastructure.services.jwt_service import JWTService


class IdentityProvider:
    def __init__(
        self,
        access_token: AccessToken,
        user_gateway: UserGateway,
        jwt_service: JWTService,
        idp_service: IDPService
    ):
        self.access_token = access_token
        self.user_gateway = user_gateway
        self.jwt_service = jwt_service
        self.idp_service = idp_service

    def get_payload(self) -> AccessTokenPayload:
        if not self.access_token:
            raise UnauthorizedError
        return self.jwt_service.decode(self.access_token)

    async def get_user_from_idp_service(self):
        return await self.idp_service.get_user_data()

    async def get_current_user_id(self, *, ok_unauthorized: bool = False) -> UUID | None:
        if not self.access_token:
            raise UnauthorizedError
        payload = self.get_payload()
        user_id = payload["sub"]
        user = await self.user_gateway.find_user_by_id(user_id)
        if user is None:
            if ok_unauthorized:
                return None
            else:
                raise UnauthorizedError

        return user.id

    async def get_current_user(self) -> User:
        user_id = await self.get_current_user_id()

        user = await self.user_gateway.find_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError(by="id")

        return user

    def check_is_user_moderator(self, user) -> bool:
        return user.role in RECIPE_MODERATOR_ROLES

    async def get_moderator_or_raise(self) -> User:
        user_id = await self.get_current_user_id()

        user = await self.user_gateway.find_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError(by="id")

        if not self.check_is_user_moderator(user):
            raise PermissionDeniedError("you are not a moderator")

        return user
