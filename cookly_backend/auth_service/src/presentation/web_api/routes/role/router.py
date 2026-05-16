from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from application.role.create_role_handler import (
    CreateRoleCommand,
    CreateRoleHandler,
)
from application.role.delete_role_handler import (
    DeleteRoleCommand,
    DeleteRoleHandler,
)
from application.role.upd_role_command_handler import (
    UpdateRoleCommand,
    UpdateRoleHandler,
)
from presentation.web_api.routes.role.schemas import UpdateRole

role_router = APIRouter(route_class=DishkaRoute, tags=["role"], prefix="/role")


@role_router.post("")
async def create_role(
    command: CreateRoleCommand, handler: FromDishka[CreateRoleHandler]
) -> ORJSONResponse:
    role_id = await handler.handle(command)
    return ORJSONResponse({"role_id": role_id}, status_code=HTTP_201_CREATED)


@role_router.put("/{role_id}")
async def update_role(
    role_id: int,
    command: UpdateRole,
    handler: FromDishka[UpdateRoleHandler],
) -> ORJSONResponse:
    data = command.model_dump()
    data.update({"role_id": role_id})
    command = UpdateRoleCommand(**data)
    await handler.handle(command)
    return ORJSONResponse({"status": "success"}, status_code=HTTP_200_OK)


@role_router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    handler: FromDishka[DeleteRoleHandler],
) -> ORJSONResponse:
    await handler.handle(DeleteRoleCommand(role_id=role_id))
    return ORJSONResponse({"status": "success"}, status_code=HTTP_200_OK)
