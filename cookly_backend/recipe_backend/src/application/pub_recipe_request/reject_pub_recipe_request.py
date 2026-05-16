from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.pub_recipe_request.common.service import PubRecipeRequestService


class RejectPubRecipeRequestHandler:
    def __init__(
        self,
        pub_recipe_request_service: PubRecipeRequestService,
        idp: IdentityProvider,
        uow: Uow
    ):
        self.pub_recipe_request_service = pub_recipe_request_service
        self.idp = idp
        self.uow = uow

    async def handle(self, pub_recipe_request_id: int, feedback: str):
        moderator = await self.idp.get_moderator_or_raise()
        await self.pub_recipe_request_service.reject_recipe_request(
            pub_recipe_request_id,
            moderator.id,
            feedback
        )
        await self.uow.commit()
