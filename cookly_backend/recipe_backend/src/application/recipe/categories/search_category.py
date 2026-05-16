from infrastructure.db.gateways.recipe_gateway import RecipeGateway


class SearchRecipeCategoryHandler:
    def __init__(self, recipe_gateway: RecipeGateway):
        self.recipe_gateway = recipe_gateway

    async def handle(self, query: str):
        return await self.recipe_gateway.search_categories(query)
