from application.common.errors.exceptions import NotFoundError, PermissionDeniedError
from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.pub_recipe_request.common.service import PubRecipeRequestService
from infrastructure.db.gateways.pub_recipe_request import PubRecipeRequestGateway


class DeletePubRecipeRequestHandler:
    def __init__(
        self,
        pub_recipe_request_service: PubRecipeRequestService,
        idp: IdentityProvider,
        uow: Uow,
        pub_recipe_request_gateway: PubRecipeRequestGateway,
    ):
        self.pub_recipe_request_service = pub_recipe_request_service
        self.idp = idp
        self.uow = uow
        self.pub_recipe_request_gateway = pub_recipe_request_gateway

    async def handle(self, pub_recipe_request_id: int):
        user_id = await self.idp.get_current_user_id()
        pub_recipe_request = await self.pub_recipe_request_gateway.get_by_id(pub_recipe_request_id)
        if not pub_recipe_request:
            raise NotFoundError("pub recipe request does not exist")
        if not pub_recipe_request.author_id == user_id:
            raise PermissionDeniedError("can't delete not your pub recipe request")
        await self.pub_recipe_request_gateway.delete(pub_recipe_request)
        await self.uow.commit()
