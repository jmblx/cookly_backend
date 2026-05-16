from application.auth.common.errors import UnauthorizedError
from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from infrastructure.db.gateways.user_gateway import UserGateway
from infrastructure.db.models import User


class LoginHandler:
    def __init__(self, idp: IdentityProvider, uow: Uow, user_gateway: UserGateway):
        self.uow = uow
        self.user_gateway = user_gateway
        self.idp = idp

    async def handle(self):
        if not (payload := self.idp.get_payload()):
            raise UnauthorizedError

        user = await self.user_gateway.find_user_by_id(payload["sub"])
        if not user:
            user_data = await self.idp.get_user_from_idp_service()
            user = User(id=user_data["id"], email=user_data["email"])
            await self.user_gateway.save(user)
        await self.uow.commit()
