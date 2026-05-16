from application.recipe.common.service import RecipeService
from presentation.web_api.routes.recipe.schemas import SearchRecipeQuery


class SearchRecipesHandler:
    def __init__(self, recipe_service: RecipeService):
        self.recipe_service = recipe_service

    async def handle(
        self,
        query: SearchRecipeQuery
    ):
        return await self.recipe_service.search_recipes(
            query
        )
