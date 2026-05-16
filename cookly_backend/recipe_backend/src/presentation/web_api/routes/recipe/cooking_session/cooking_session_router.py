from typing import Annotated

from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)
from fastapi import APIRouter, Body
from starlette import status

from application.recipe.cooking_sessions.cancel_cooking_session import CancelCookingSessionHandler
from application.recipe.cooking_sessions.change_active_step import ChangeStepCookingSessionHandler
from application.recipe.cooking_sessions.finish_cooking_session import FinishCookingSessionHandler
from application.recipe.cooking_sessions.get_user_active_session import GetUserCookingSessionHandler
from application.recipe.cooking_sessions.start_cooking_session import StartCookingSessionHandler
from presentation.web_api.routes.recipe.cooking_session.schemas import (
    ActiveCookingSessionResponse,
    StartCookingSessionResponse,
)

cooking_session_router = APIRouter(
    prefix="",
    tags=["cooking_session"],
    route_class=DishkaRoute
)


@cooking_session_router.post("/recipe/{recipe_id}/cooking_session/start",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {"description": r"Started\Existing recipe cooking session created. Returns its id"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def start_cooking_session(
    handler: FromDishka[StartCookingSessionHandler],
    recipe_id: int,
) -> StartCookingSessionResponse:
    cooking_session_id = await handler.handle(
        recipe_id
    )

    return StartCookingSessionResponse(cooking_session_id=cooking_session_id)


@cooking_session_router.get("/cooking-sessions/active",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {"description": r"Returns active cooking sessions with recipe step where user stopped"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def get_active_cooking_sessions(
    handler: FromDishka[GetUserCookingSessionHandler],
) -> list[ActiveCookingSessionResponse]:
    active_cooking_sessions_data = await handler.handle()
    return [ActiveCookingSessionResponse(**data) for data in active_cooking_sessions_data]


@cooking_session_router.post("/cooking-sessions/{cooking_session_id}/change-active-step",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": r"Change active step of recipe cooking session created. No response content"
        },
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def change_current_active_step_cooking_session(
    handler: FromDishka[ChangeStepCookingSessionHandler],
    cooking_session_id: int,
    new_step_id: Annotated[int, Body()]
):
    await handler.handle(
        cooking_session_id, new_step_id
    )


@cooking_session_router.post("/cooking-sessions/{cooking_session_id}/cancel",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": r"Cancel recipe cooking session created. No response content"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def cancel_cooking_session(
    handler: FromDishka[CancelCookingSessionHandler],
    cooking_session_id: int,
):
    await handler.handle(
        cooking_session_id
    )


@cooking_session_router.post("/cooking-sessions/{cooking_session_id}/finish",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": r"Finish recipe cooking session created. No response content"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def finish_cooking_session(
    handler: FromDishka[FinishCookingSessionHandler],
    cooking_session_id: int,
):
    await handler.handle(
        cooking_session_id
    )
