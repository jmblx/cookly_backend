
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status
from starlette.responses import Response

from application.pub_recipe_request.approve_pub_recipe_request import ApprovePubRecipeRequestHandler
from application.pub_recipe_request.delete_pub_recipe_request import DeletePubRecipeRequestHandler
from application.pub_recipe_request.reject_pub_recipe_request import RejectPubRecipeRequestHandler
from application.pub_recipe_request.request_publish_request import CreateRequestPublishRecipeHandler
from presentation.web_api.routes.recipe.pub_recipe_request.schemas import (
    PublishRecipeRequestResponse,
    RejectPubRecipeRequestData,
)

pub_recipe_request_router = APIRouter(
    prefix="",
    tags=["pub recipe request"],
    route_class=DishkaRoute
)


@pub_recipe_request_router.post("/recipe/{recipe_id}/request-publish",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {"description": r"Creating request to publish recipe. Returns its id"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def pub_recipe_request_create(
    handler: FromDishka[CreateRequestPublishRecipeHandler],
    recipe_id: int,
) -> PublishRecipeRequestResponse:
    pub_recipe_request_id = await handler.handle(
        recipe_id
    )

    return PublishRecipeRequestResponse(pub_recipe_request_id=pub_recipe_request_id)


@pub_recipe_request_router.post("/pub-recipe-request/{pub_recipe_request_id}/approve",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": r"Approve publish recipe request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden. User is not moderator"},
    }
)
async def pub_recipe_request_approve(
    handler: FromDishka[ApprovePubRecipeRequestHandler],
    pub_recipe_request_id: int,
    response: Response
):
    await handler.handle(
        pub_recipe_request_id
    )
    response.status_code = status.HTTP_204_NO_CONTENT


@pub_recipe_request_router.post("/pub-recipe-request/{pub_recipe_request_id}/reject",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": r"Reject publish recipe request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden. User is not moderator"},
    }
)
async def pub_recipe_request_reject(
    handler: FromDishka[RejectPubRecipeRequestHandler],
    pub_recipe_request_id: int,
    reject_data: RejectPubRecipeRequestData,
    response: Response
):
    await handler.handle(
        pub_recipe_request_id,
        reject_data.feedback
    )
    response.status_code = status.HTTP_204_NO_CONTENT


@pub_recipe_request_router.delete(
    "/{pub_recipe_request_id}",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Deleted"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
)
async def delete_pub_recipe_request(
    handler: FromDishka[DeletePubRecipeRequestHandler],
    pub_recipe_request_id: int,
    response: Response
):
    await handler.handle(pub_recipe_request_id)
    response.status_code = status.HTTP_204_NO_CONTENT
