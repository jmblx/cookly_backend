from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.pub_recipe_request.common.service import PubRecipeRequestService
from application.recipe.common.service import RecipeService
from presentation.web_api.routes.recipe.schemas import RecipeFullRequest


class UpdateRecipeHandler:
    def __init__(
        self,
        uow: Uow,
        recipe_service: RecipeService,
        idp: IdentityProvider,
        pub_recipe_request_service: PubRecipeRequestService
    ):
        self.uow = uow
        self.recipe_service = recipe_service
        self.idp = idp
        self.pub_recipe_request_service = pub_recipe_request_service

    async def handle(self, recipe_id: int, data: RecipeFullRequest):
        user_id = await self.idp.get_current_user_id()
        recipe = await self.recipe_service.get_with_author_check(recipe_id, user_id)
        recipe = await self.recipe_service.update_recipe(recipe, data)

        await self.pub_recipe_request_service.renew_recipe_pub_rq_if_exists(recipe)
        await self.uow.commit()
        return recipe
