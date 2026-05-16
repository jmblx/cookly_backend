from application.common.idp import IdentityProvider
from infrastructure.db.gateways.ingredient_gateway import IngredientGateway
from infrastructure.db.models import IngredientGroup


class GetAllIngredientGroupsHandler:
    def __init__(self, ingredient_gateway: IngredientGateway, idp: IdentityProvider):
        self.ingredient_gateway = ingredient_gateway
        self.idp = idp

    async def handle(self) -> list[dict[str, IngredientGroup | bool]]:
        return await self.ingredient_gateway.get_all_ingredient_groups_with_user_selected_data(
            await self.idp.get_current_user_id()
        )
