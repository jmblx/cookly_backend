from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette.status import HTTP_201_CREATED

from application.strategy.create_new_strategy.create_new_hanlder import (
    CreateNewStrategyCommand,
    CreateNewStrategyHanlder,
)
from application.strategy.read_strategy.strategy_query_handler import (
    StrategyQueryHandler,
)
from infrastructure.db.readers.strategy_reader import ReadStrategyDTO

strategy_router = APIRouter(route_class=DishkaRoute, tags=["strategy"])


@strategy_router.post("/strategy")
async def add_strategy(
    handler: FromDishka[CreateNewStrategyHanlder],
    command: CreateNewStrategyCommand,
) -> ORJSONResponse:
    return ORJSONResponse(
        {"strategy_id": await handler.handle(command)},
        status_code=HTTP_201_CREATED,
    )


@strategy_router.get("/strategy/{strategy_id}")
async def get_strategy(
    strategy_id: UUID, handler: FromDishka[StrategyQueryHandler]
) -> ReadStrategyDTO:
    return await handler.handle(strategy_id)
