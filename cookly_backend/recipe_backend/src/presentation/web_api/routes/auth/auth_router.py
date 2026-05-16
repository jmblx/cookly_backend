from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)
from fastapi import APIRouter
from starlette import status

from application.auth.login_handler import LoginHandler

auth_router = APIRouter(prefix="/auth", tags=["auth"], route_class=DishkaRoute)


@auth_router.get("/login", responses={
    status.HTTP_204_NO_CONTENT: {"description": "OK"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
})
async def login(handler: FromDishka[LoginHandler]):
    await handler.handle()
