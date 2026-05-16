from typing import Annotated, cast

from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)
from fastapi import APIRouter, Query
from pydantic import EmailStr
from starlette import status
from starlette.responses import Response

from application.common.idp import IdentityProvider
from application.recipe.get_feed import GetFeedHandler
from application.recipe.get_meal_tt_feed import GetMealTimeTypeFeedHandler
from application.user.get_favorites import GetUserFavoriteRecipesHandler
from application.user.get_history import GetUserRecipeHistoryHandler
from application.user.set_excluded_ingredient_groups import SetExcludedIngredientGroupsHandler
from core.config import MinioConfig
from domain.entities.value_objects import MealTimeType
from infrastructure.db.gateways.user_gateway import UserGateway
from presentation.web_api.routes.auth.schemas import MeResponse
from presentation.web_api.routes.recipe.schemas import DefaultRecipesResponse, FeedPaginationParams, FeedResponse
from presentation.web_api.routes.user.schemas import IngredientGroupIds

user_router = APIRouter(prefix="/user", tags=["user"], route_class=DishkaRoute)


@user_router.get(
    "/me",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {"description": "User data"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def get_me(identity: FromDishka[IdentityProvider], minio_config: FromDishka[MinioConfig]) -> MeResponse:
    user = await identity.get_current_user()
    return MeResponse(
        id=user.id,
        email=cast(EmailStr, user.email),
        role=user.role,
        avatar_url=f"{minio_config.url}/{minio_config.user_avatar_bucket_name}/{user.id}.webp"
    )


@user_router.put(
    "/exclude-ingredients-groups",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Ingredients groups excluded from user settings replaced by new one"
        },
    }
)
async def set_exclude_ingredients_groups(
    handler: FromDishka[SetExcludedIngredientGroupsHandler],
    groups_ids_data: IngredientGroupIds,
    response: Response
):
    await handler.handle(groups_ids_data.ingredient_group_ids)
    response.status_code = status.HTTP_204_NO_CONTENT


@user_router.get(
    "/feed",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "User data",
        }
    }
)
async def get_feed(
    handler: FromDishka[GetFeedHandler],
    pagination_params: Annotated[FeedPaginationParams, Query()],
) -> FeedResponse:
    recipes_feed_data = await handler.handle(
        pagination_params.last_score,
        pagination_params.last_id,
        pagination_params.pagination_key,
        pagination_params.limit,
    )
    return FeedResponse(
        recipes=recipes_feed_data[0],
        last_recipe_score=recipes_feed_data[1],
        last_recipe_id=recipes_feed_data[2],
        pagination_key=recipes_feed_data[3]
    )


@user_router.get(
    "/feed/{meal_time_type}",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "User data",
        }
    }
)
async def get_mtt_feed(
    handler: FromDishka[GetMealTimeTypeFeedHandler],
    meal_time_type: MealTimeType,
    pagination_params: Annotated[FeedPaginationParams, Query()],
) -> FeedResponse:
    recipes_mtt_feed = await handler.handle(
        pagination_params.last_score,
        pagination_params.last_id,
        pagination_params.pagination_key,
        pagination_params.limit,
        meal_time_type,
    )
    return FeedResponse(
        recipes=recipes_mtt_feed[0],
        last_recipe_score=recipes_mtt_feed[1],
        last_recipe_id=recipes_mtt_feed[2],
        pagination_key=recipes_mtt_feed[3]
    )


@user_router.get(
    "/recipe-history",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "User recipe history data",
        }
    }
)
async def get_user_recipe_history(
    handler: FromDishka[GetUserRecipeHistoryHandler],
) -> DefaultRecipesResponse:
    recipes = await handler.handle()
    return DefaultRecipesResponse(
        recipes=recipes,
    )


@user_router.get(
    "/favorite-recipes",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "User data",
        }
    }
)
async def get_user_favorite_recipes(
    handler: FromDishka[GetUserFavoriteRecipesHandler],
) -> DefaultRecipesResponse:
    recipes = await handler.handle()
    return DefaultRecipesResponse(
        recipes=recipes,
    )


@user_router.get(
    "/saved-recipes",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "Saved user recipes",
        }
    }
)
async def get_user_saved_recipes(
    user_reader: FromDishka[UserGateway],
    idp: FromDishka[IdentityProvider],
) -> DefaultRecipesResponse:
    user_id = await idp.get_current_user_id()
    recipes = await user_reader.get_user_saved_recipes(user_id)
    return DefaultRecipesResponse(
        recipes=recipes,
    )

@user_router.get(
    "/moderating-recipes",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "Moderating user recipes",
        }
    }
)
async def get_user_moderating_recipes(
    user_reader: FromDishka[UserGateway],
    idp: FromDishka[IdentityProvider],
) -> DefaultRecipesResponse:
    user_id = await idp.get_current_user_id()
    recipes = await user_reader.get_user_moderating_recipes(user_id)
    return DefaultRecipesResponse(
        recipes=recipes,
    )


@user_router.get(
    "/rejected-recipes",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "Rejected user recipes",
        }
    }
)
async def get_user_rejected_recipes(
    user_reader: FromDishka[UserGateway],
    idp: FromDishka[IdentityProvider],
) -> DefaultRecipesResponse:
    user_id = await idp.get_current_user_id()
    recipes = await user_reader.get_user_rejected_recipes(user_id)
    return DefaultRecipesResponse(
        recipes=recipes,
    )


@user_router.get(
    "/published-recipes",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "Published user recipes",
        }
    }
)
async def get_user_published_recipes(
    user_reader: FromDishka[UserGateway],
    idp: FromDishka[IdentityProvider],
) -> DefaultRecipesResponse:
    user_id = await idp.get_current_user_id()
    recipes = await user_reader.get_user_published_recipes(user_id)
    return DefaultRecipesResponse(
        recipes=recipes,
    )
