from dishka import Provider, Scope, provide

from infrastructure.db.gateways.cooking_session_gateway import CookingSessionGateway
from infrastructure.db.gateways.ingredient_gateway import IngredientGateway
from infrastructure.db.gateways.pub_recipe_request import PubRecipeRequestGateway
from infrastructure.db.gateways.recipe_gateway import RecipeGateway
from infrastructure.db.gateways.user_gateway import UserGateway


class GatewayProvider(Provider):
    user_gateway = provide(UserGateway, scope=Scope.REQUEST)
    recipe_gateway = provide(RecipeGateway, scope=Scope.REQUEST)
    ingredient_gateway = provide(IngredientGateway, scope=Scope.REQUEST)
    cooking_session_gateway = provide(CookingSessionGateway, scope=Scope.REQUEST)
    pub_recipe_request_gateway = provide(PubRecipeRequestGateway, scope=Scope.REQUEST)
