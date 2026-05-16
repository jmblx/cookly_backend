from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette import status

from application.user.confirm_email_handler import (
    ConfirmEmailCommand,
    ConfirmEmailHandler,
)

email_conf_router = APIRouter(route_class=DishkaRoute, tags=["auth"])


@email_conf_router.post("/confirm-email/{conf_token}")
async def confirm_email(
    conf_token: str, handler: FromDishka[ConfirmEmailHandler]
):
    command = ConfirmEmailCommand(conf_token)
    await handler.handle(command)
    return ORJSONResponse(
        {"status": "success"}, status_code=status.HTTP_204_NO_CONTENT
    )
