import logging
import os
from contextlib import asynccontextmanager
from dataclasses import asdict

from dishka.integrations.fastapi import (
    setup_dishka,
)
from fastapi import FastAPI

from core.di.container import container
from infrastructure.log.main import configure_logging
from presentation.web_api.config import load_config
from presentation.web_api.exceptions import setup_exception_handlers
from presentation.web_api.middlewares import setup_middlewares
from presentation.web_api.routes.auth.router import auth_router
from presentation.web_api.routes.auth_server_token_manage.router import (
    token_manage_router,
)
from presentation.web_api.routes.client.client_router import client_router
from presentation.web_api.routes.client.refs.router import client_ref_router
from presentation.web_api.routes.client_token_manage.client_token_manage_router import (
    client_token_manage_router,
)
from presentation.web_api.routes.email_confirmation.router import (
    email_conf_router,
)
from presentation.web_api.routes.healthcheck.router import healthcheck_router
from presentation.web_api.routes.registration.router import reg_router
from presentation.web_api.routes.resource_server.router import rs_router
from presentation.web_api.routes.role.router import role_router
from presentation.web_api.routes.third_party_providers.router import (
    third_party_router,
)
from presentation.web_api.routes.user_account.router import user_account_router
from presentation.web_api.routes.user_password.router import (
    user_password_router,
)


@asynccontextmanager  # type: ignore
async def lifespan(app: FastAPI) -> None:  # type: ignore
    yield
    await app.state.dishka_container.close()  # type: ignore


logger = logging.getLogger(__name__)

# logstash_handler = TCPLogstashHandler("logstash", 50000)
# logger.addHandler(logstash_handler)


config = load_config()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        root_path="/api",
    )
    app.include_router(third_party_router)
    app.include_router(reg_router)
    app.include_router(client_router)
    app.include_router(auth_router)
    app.include_router(role_router)
    app.include_router(token_manage_router)
    app.include_router(healthcheck_router)
    app.include_router(email_conf_router)
    app.include_router(user_password_router)
    app.include_router(user_account_router)
    app.include_router(rs_router)
    app.include_router(client_token_manage_router)
    app.include_router(client_ref_router)
    setup_exception_handlers(app)
    setup_middlewares(app)
    return app


def create_production_app():
    app = create_app()
    setup_dishka(container=container, app=app)
    return app


if os.getenv("GUNICORN_MAIN", "false").lower() not in ("false", "0"):

    def main():
        from presentation.web_api.gunicorn.application import Application

        configure_logging(config.app_logging_config)

        gunicorn_app = Application(
            application=create_production_app(),
            options={
                **asdict(config.gunicorn_config),
                "logconfig_dict": config.app_logging_config,
            },
        )
        gunicorn_app.run()

    if __name__ == "__main__":
        main()

else:
    configure_logging(config.app_logging_config)
    app = create_production_app()
