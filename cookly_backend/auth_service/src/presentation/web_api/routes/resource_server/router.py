from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.params import Param
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.responses import Response

from application.common.views.rs_view import ResourceServerIdsData, ResourceServerIdsViewData
from application.resource_server.dtos import ResourceServerCreateDTO
from application.resource_server.find_rs import FindRSHandler, FindRSQuery
from application.resource_server.get_all_resource_servers import (
    GetAllRSIdsHandler,
    GetRSIdsQuery,
)
from application.resource_server.read_rs_view_handler import (
    ReadResourceServerPageViewQuery,
    ReadResourceServerPageViewQueryHandler,
)
from application.resource_server.register_rs_handler import (
    RegisterResourceServerCommand,
    RegisterResourceServerHandler,
)
from application.resource_server.update_rs_handler import (
    UpdateResourceServerCommand,
    UpdateResourceServerHandler,
)
from domain.entities.resource_server.value_objects import ResourceServerID
from presentation.web_api.common.schemas import PaginationData
from presentation.web_api.routes.resource_server.models import (
    ResourceServerViewModel,
    UpdateResourceServerModel,
)

rs_router = APIRouter(
    route_class=DishkaRoute, tags=["resource_server"], prefix="/rs"
)


@rs_router.post("")
async def register_rs(
    command: RegisterResourceServerCommand,
    handler: FromDishka[RegisterResourceServerHandler],
    response: Response,
) -> ResourceServerCreateDTO:
    response.status_code = status.HTTP_201_CREATED
    rs = await handler.handle(command)
    return rs


@rs_router.get("/search")
async def search_client_by_input(
    search_input: str,
    handler: FromDishka[FindRSHandler],
) -> ResourceServerIdsViewData:
    return await handler.handle(FindRSQuery(search_input=search_input))


@rs_router.get("/ids_data")
async def get_rs_ids(
    handler: FromDishka[GetAllRSIdsHandler],
    pagination_data: Annotated[PaginationData, Param()],
) -> ResourceServerIdsViewData:
    resource_server_ids_data = await handler.handle(
        GetRSIdsQuery(
            after_id=pagination_data.after_id,
            page_size=pagination_data.page_size,
        )
    )
    return resource_server_ids_data


@rs_router.put("/{rs_id}")
async def update_rs(
    rs_id: int,
    command: UpdateResourceServerModel,
    handler: FromDishka[UpdateResourceServerHandler],
) -> ORJSONResponse:
    command = UpdateResourceServerCommand(rs_id=rs_id, **command.model_dump())
    await handler.handle(command)
    return ORJSONResponse(
        {"status": "success"}, status_code=status.HTTP_200_OK
    )


@rs_router.get("/{rs_id}")
async def get_rs(
    rs_id: int, handler: FromDishka[ReadResourceServerPageViewQueryHandler]
) -> ResourceServerViewModel:
    rs_view = await handler.handle(
        ReadResourceServerPageViewQuery(rs_id=rs_id)
    )
    return ResourceServerViewModel(**rs_view)
