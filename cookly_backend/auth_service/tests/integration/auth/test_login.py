import pytest
from dishka import AsyncContainer

from application.auth_as.login_user_auth_server import (
    AuthenticateUserCommand,
    LoginUserHandler,
)
from domain.exceptions.auth import InvalidCredentialsError


@pytest.mark.parametrize(
    "email,password,is_fall",
    [
        ("admin@test.com", "string", False),
        ("admin@test.com", "not correct", True),
    ],
)
@pytest.mark.asyncio
async def test_login(
    rq_container: AsyncContainer, email: str, password: str, is_fall: bool
):
    handler = await rq_container.get(LoginUserHandler)
    command = AuthenticateUserCommand(email, password)
    if is_fall:
        with pytest.raises(InvalidCredentialsError) as e:
            await handler.handle(command)
    else:
        result = await handler.handle(command)
        refresh_token = result[0]["refresh_token"]
        assert refresh_token.startswith("eyJhbGciOiJSU")
        access_token = result[0]["access_token"]
        assert access_token.startswith("eyJhbGciOiJSU")
