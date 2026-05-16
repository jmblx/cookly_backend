from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from core.config import config_loader
from domain.entities.value_objects import RoleType
from infrastructure.db.gateways.user_gateway import UserGateway


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str, sessionmaker):
        super().__init__(secret_key)
        self.sessionmaker = sessionmaker

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form["username"]
        password = form["password"]
        async with self.sessionmaker() as session:
            user = await UserGateway(session).find_user_by_email(username)
        if not user:
            return False
        # password_hasher = argon2.PasswordHasher()
        # password_hasher.verify(
        #     password,
        # )
        if password not in config_loader.app_config.admin.admin_passwords.split(","):
            return False

        request.session.update({
            "user_id": str(user.id),
            "is_admin": user.role == RoleType.admin,
        })

        return True

    async def logout(self, request: Request) -> bool:
        request.session.update({
            "user_id": None,
            "is_admin": None,
        })

        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")

        return bool(user_id)
