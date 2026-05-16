import logging
from contextlib import asynccontextmanager
from dataclasses import asdict

from dishka.integrations.fastapi import (
    setup_dishka,
)
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import config_loader
from core.di.container import container
from infrastructure.log.main import configure_logging
from presentation.web_api.admin.main import setup_admin
from presentation.web_api.exceptions import setup_exception_handlers
from presentation.web_api.middlwares import setup_middlewares
from presentation.web_api.routes.auth.auth_router import auth_router
from presentation.web_api.routes.chef.router import chef_router
from presentation.web_api.routes.moderator.router import moderator_router
from presentation.web_api.routes.recipe.cooking_session.cooking_session_router import cooking_session_router
from presentation.web_api.routes.recipe.ingredient_group_router import ingredient_group_router
from presentation.web_api.routes.recipe.ingredient_router import ingredient_router
from presentation.web_api.routes.recipe.pub_recipe_request.router import pub_recipe_request_router
from presentation.web_api.routes.recipe.recipe_category_router import recipe_category_router
from presentation.web_api.routes.recipe.recipe_router import recipe_router
from presentation.web_api.routes.user.user_router import user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    yield
    await app.state.dishka_container.close()


logger = logging.getLogger(__name__)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API",
        version="1.0.0",
        description="API with Bearer auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        root_path="/api",
    )
    setup_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(recipe_router)
    app.include_router(ingredient_router)
    app.include_router(ingredient_group_router)
    app.include_router(recipe_category_router)
    app.include_router(cooking_session_router)
    app.include_router(chef_router)
    app.include_router(pub_recipe_request_router)
    app.include_router(moderator_router)
    setup_middlewares(app)
    db_conf = config_loader.app_config.database
    db_uri = f"postgresql+asyncpg://{db_conf.user}:{db_conf.password}@{db_conf.host}:{db_conf.port}/{db_conf.name}"
    engine = create_async_engine(db_uri)
    app = setup_admin(app, engine)
    app.openapi = custom_openapi
    return app


def create_production_app():
    app = create_app()
    setup_dishka(container=container, app=app)
    return app


app = create_production_app()

global_config = config_loader.app_config.global_
logging_config = config_loader.logging_config
configure_logging(logging_config)


def main():
    if not global_config.debug:
        from presentation.web_api.gunicorn_application import Application

        gunicorn_config = config_loader.app_config.gunicorn
        gunicorn_app = Application(application=app, options=asdict(gunicorn_config))
        gunicorn_app.run()


if __name__ == "__main__":
    main()
