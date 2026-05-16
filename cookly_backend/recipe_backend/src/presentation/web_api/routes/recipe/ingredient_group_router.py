from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from application.ingredient.get_all_ingredient_groups import GetAllIngredientGroupsHandler
from presentation.web_api.routes.recipe.schemas import UserIngredientGroupResponse

ingredient_group_router = APIRouter(prefix="/ingredient-group", tags=["ingredient group"], route_class=DishkaRoute)


@ingredient_group_router.get("/list", responses={
    status.HTTP_200_OK: {"description": "All ingredient groups"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
}
)
async def get_all_ingredient_groups(
    handler: FromDishka[GetAllIngredientGroupsHandler]
) -> list[UserIngredientGroupResponse]:
    groups_data = await handler.handle()
    return [
        UserIngredientGroupResponse(
            id=group_data["group"].id,
            title=group_data["group"].title,
            excluded_by_user=group_data["is_excluded_by_user"]
        ) for group_data in groups_data
    ]
