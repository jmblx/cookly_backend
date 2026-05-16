from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from presentation.web_api.admin.auth import AdminAuth
from presentation.web_api.admin.cooking_session import CookingSessionAdmin
from presentation.web_api.admin.ingredient import IngredientAdmin
from presentation.web_api.admin.ingredient_group import IngredientGroupAdmin
from presentation.web_api.admin.pub_recipe_request import PubRecipeRequestAdmin
from presentation.web_api.admin.recipe import RecipeAdmin
from presentation.web_api.admin.recipe_category import RecipeCategoryAdmin
from presentation.web_api.admin.recipe_step import RecipeStepAdmin
from presentation.web_api.admin.user import UserAdmin
from presentation.web_api.config import data


def setup_admin(app, engine):
    sessionmaker = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    authentication_backend = AdminAuth(data.get("global").get("secret"), sessionmaker)
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(IngredientAdmin)
    admin.add_view(IngredientGroupAdmin)
    admin.add_view(RecipeAdmin)
    admin.add_view(RecipeStepAdmin)
    admin.add_view(RecipeCategoryAdmin)
    admin.add_view(PubRecipeRequestAdmin)
    admin.add_view(CookingSessionAdmin)

    return app
