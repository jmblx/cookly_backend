import typing

from sqladmin import ModelView

from infrastructure.db.models import IngredientGroup


class IngredientGroupAdmin(ModelView, model=IngredientGroup):
    name = "Группа ингредиентов"
    name_plural = "Группы ингредиентов"

    column_list: typing.ClassVar = [
        IngredientGroup.id,
        IngredientGroup.title,
    ]
    column_details_list: typing.ClassVar = [
        IngredientGroup.id,
        IngredientGroup.title,
        IngredientGroup.ingredients,
    ]
