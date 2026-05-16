from typing import Annotated
from urllib.parse import unquote

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.params import Param
from fastapi.responses import ORJSONResponse
from starlette.status import HTTP_204_NO_CONTENT

from application.client.add_allowed_url import (
    AddAllowedRedirectUrlCommand,
    AddAllowedRedirectUrlCommandHandler,
)
from application.client.avatar_query import GetClientAvatarHandler
from application.client.client_queries import (
    ClientAuthResponse,
    ClientAuthValidationQueryHandler,
    ValidateClientRequest,
)
from application.client.client_ref.common.repo import SaveRefDTO
from application.client.client_ref.create_ref_handler import RegisterRefHandler, RegisterRefCommand
from application.client.client_ref.read_ref_view_data_handler import ReadRefPageViewQueryHandler
from application.client.client_ref.update_ref_handler import UpdateRefCommand, UpdateRefCommandHandler
from application.client.find_clients import (
    FindClientsHandler,
    FindClientsQuery,
)
from application.client.get_all_clients import (
    GetClientsIdsHandler,
    GetClientsIdsQuery,
)
from application.client.read_client_view_handler import (
    ReadClientPageViewQuery,
    ReadClientPageViewQueryHandler,
)
from application.client.register_client_hadler import (
    RegisterClientCommand,
    RegisterClientHandler,
)
from application.client.set_client_avatar_handler import (
    SetClientAvatarCommand,
    SetClientAvatarHandler,
)
from application.client.update_client import (
    UpdateClientCommand,
    UpdateClientCommandHandler,
)
from application.common.views.client_view import ClientsIdsData
from application.dtos.client import ClientCreateDTO
from application.dtos.set_image import ImageDTO
from domain.entities.client.value_objects import ClientID
from presentation.web_api.common.schemas import PaginationData
from presentation.web_api.routes.client.models import (
    ClientAuthResponseModel,
    ClientViewModel,
    UpdateClientModel,
)
from presentation.web_api.routes.client.refs.models import RegisterRefData, RefView, UpdateRefModel

client_ref_router = APIRouter(
    prefix="/client", route_class=DishkaRoute, tags=["client_refs"]
)


@client_ref_router.post("/{client_id}/refs")
async def create_client_ref(
    client_id: int, data: RegisterRefData, handler: FromDishka[RegisterRefHandler]
) -> SaveRefDTO:
    command = RegisterRefCommand(**data.model_dump(), client_id=client_id)
    client = await handler.handle(command)
    return client


@client_ref_router.put("/{client_id}/refs/{ref_id}")
async def update_client_ref(
    client_id: int,
    ref_id: int,
    command_data: UpdateRefModel,
    handler: FromDishka[UpdateRefCommandHandler],
) -> ORJSONResponse:
    data = command_data.model_dump()
    data.update({"ref_id": ref_id})
    command = UpdateRefCommand(**data)
    await handler.handle(command)
    return ORJSONResponse(
        {"status": "success"}, status_code=HTTP_204_NO_CONTENT
    )
#
#
# @client_ref_router.get("/ids_data")
# async def get_client_ref_ids(
#     client_id: int,
#     handler: FromDishka[GetClientsIdsHandler],
# ) -> dict[ClientID, ClientsIdsData]:
#     query = GetClientsIdsQuery(
#
#     )
#     client_ids_data = await handler.handle(query)
#     return client_ids_data


@client_ref_router.get("/refs/{ref_id}")
async def get_client_ref(
    ref_id: int,
    handler: FromDishka[ReadRefPageViewQueryHandler],
) -> RefView:
    return await handler.handle(
        ref_id=ref_id
    )
