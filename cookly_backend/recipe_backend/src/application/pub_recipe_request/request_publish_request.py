from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.pub_recipe_request.common.service import PubRecipeRequestService
from application.recipe.common.exceptions import RecipeAlreadyPublishedError, RecipeNotFoundError
from infrastructure.db.gateways.recipe_gateway import RecipeGateway


class CreateRequestPublishRecipeHandler:
    def __init__(
        self,
        pub_rq_service: PubRecipeRequestService,
        idp: IdentityProvider,
        uow: Uow,
        recipe_gateway: RecipeGateway
    ):
        self.pub_rq_service = pub_rq_service
        self.idp = idp
        self.uow = uow
        self.recipe_gateway = recipe_gateway

    async def handle(self, recipe_id: int) -> int:
        user = await self.idp.get_current_user()
        recipe = await self.recipe_gateway.get_by_id(recipe_id)

        if not recipe:
            raise RecipeNotFoundError

        if recipe.is_public:
            raise RecipeAlreadyPublishedError

        pub_recipe_request_id = await self.pub_rq_service.create_pub_recipe_request(user.id, recipe_id)
        if self.idp.check_is_user_moderator(user):
            await self.pub_rq_service.approve_recipe_request(pub_recipe_request_id, user.id)

        await self.uow.commit()
        return pub_recipe_request_id
