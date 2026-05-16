from infrastructure.db.gateways.ingredient_gateway import IngredientGateway


class SearchIngredientsHandler:
    def __init__(self, ingredient_gateway: IngredientGateway):
        self.ingredient_gateway = ingredient_gateway

    async def handle(self, query: str):
        return await self.ingredient_gateway.search_ingredients(query)

